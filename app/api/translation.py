"""
Translation API endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db
from app.models.models import User, TranslationSession, UserProgress
from app.services.translation_coach import TranslationCoachService
from app.utils.validators import validate_translation_request, validate_language_code
from app.utils.decorators import rate_limit
import logging

logger = logging.getLogger(__name__)

translation_bp = Blueprint('translation', __name__, url_prefix='/api/translation')


@translation_bp.route('/analyze', methods=['POST'])
@jwt_required()
@rate_limit('30 per hour')
def analyze_translation():
    """
    Analyze a translation request and generate guided questions.
    
    POST /api/translation/analyze
    Body: {
        "source_text": "I went to the store yesterday",
        "source_language": "en",
        "target_language": "es",
        "difficulty": "intermediate"  # optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate request
        validation_error = validate_translation_request(data)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        source_text = data['source_text']
        source_lang = data['source_language']
        target_lang = data['target_language']
        difficulty = data.get('difficulty', 'intermediate')
        
        # Get current user
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Initialize translation coach
        coach = TranslationCoachService()
        
        # Analyze translation request
        analysis = coach.analyze_translation_request(
            source_text=source_text,
            source_lang=source_lang,
            target_lang=target_lang,
            difficulty=difficulty
        )
        
        # Create translation session
        session = TranslationSession(
            user_id=user_id,
            source_text=source_text,
            source_language=source_lang,
            target_language=target_lang,
            ai_questions=analysis['questions'],
            correct_translation=analysis['correct_translation'],
            grammar_points=analysis['grammar_concepts'],
            vocabulary_suggestions=analysis['vocabulary_focus'],
            difficulty_level=difficulty,
            started_at=datetime.utcnow()
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Return analysis without correct_translation (student shouldn't see it yet)
        response = {
            'session_id': session.id,
            'source_text': analysis['source_text'],
            'source_language': analysis['source_language'],
            'target_language': analysis['target_language'],
            'questions': analysis['questions'],
            'grammar_concepts': analysis['grammar_concepts'],
            'vocabulary_focus': analysis['vocabulary_focus'],
            'common_mistakes': analysis['common_mistakes'],
            'difficulty': difficulty
        }
        
        logger.info(f"Translation analysis created for user {user_id}, session {session.id}")
        return jsonify(response), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        logger.error(f"Translation service error: {str(e)}")
        return jsonify({'error': 'Translation service unavailable'}), 503
    except Exception as e:
        logger.error(f"Unexpected error in analyze_translation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@translation_bp.route('/submit', methods=['POST'])
@jwt_required()
@rate_limit('60 per hour')
def submit_translation():
    """
    Submit a translation attempt and get evaluation.
    
    POST /api/translation/submit
    Body: {
        "session_id": "uuid",
        "user_translation": "Fui a la tienda ayer",
        "time_spent_seconds": 120,
        "hints_requested": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('session_id') or not data.get('user_translation'):
            return jsonify({'error': 'session_id and user_translation are required'}), 400
        
        session_id = data['session_id']
        user_translation = data['user_translation'].strip()
        time_spent = data.get('time_spent_seconds', 0)
        hints_requested = data.get('hints_requested', 0)
        
        # Get current user
        user_id = get_jwt_identity()
        
        # Get translation session
        session = TranslationSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Translation session not found'}), 404
        
        if session.completed:
            return jsonify({'error': 'Session already completed'}), 400
        
        # Evaluate translation
        coach = TranslationCoachService()
        evaluation = coach.evaluate_user_translation(
            source_text=session.source_text,
            user_translation=user_translation,
            source_lang=session.source_language,
            target_lang=session.target_language,
            correct_translation=session.correct_translation
        )
        
        # Update session
        session.user_translation = user_translation
        session.accuracy_score = evaluation['accuracy_score']
        session.grammar_score = evaluation['grammar_score']
        session.vocabulary_score = evaluation['vocabulary_score']
        session.time_spent_seconds = time_spent
        session.hints_requested = hints_requested
        session.completed = True
        session.completed_at = datetime.utcnow()
        
        # Update user progress
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            language=session.target_language
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                language=session.target_language
            )
            db.session.add(progress)
        
        # Update progress metrics
        progress.total_sessions += 1
        progress.completed_sessions += 1
        
        # Update average accuracy
        total_accuracy = (progress.average_accuracy * (progress.completed_sessions - 1) + 
                         evaluation['accuracy_score'])
        progress.average_accuracy = total_accuracy / progress.completed_sessions
        
        # Update learning streak
        today = datetime.utcnow().date()
        if progress.last_practice_date:
            days_diff = (today - progress.last_practice_date).days
            if days_diff == 1:
                progress.current_streak_days += 1
            elif days_diff > 1:
                progress.current_streak_days = 1
        else:
            progress.current_streak_days = 1
        
        progress.last_practice_date = today
        progress.longest_streak_days = max(
            progress.longest_streak_days,
            progress.current_streak_days
        )
        
        # Add mastered grammar points
        if evaluation['accuracy_score'] >= 90:
            for concept in session.grammar_points:
                if concept not in progress.mastered_grammar_points:
                    progress.mastered_grammar_points.append(concept)
        
        db.session.commit()
        
        # Prepare response
        response = {
            'session_id': session.id,
            'evaluation': evaluation,
            'correct_translation': session.correct_translation,
            'your_translation': user_translation,
            'progress_update': progress.to_dict()
        }
        
        logger.info(f"Translation submitted for session {session_id}, score: {evaluation['accuracy_score']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in submit_translation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@translation_bp.route('/hints/<session_id>', methods=['GET'])
@jwt_required()
def get_hints(session_id):
    """
    Get progressive hints for a translation session.
    
    GET /api/translation/hints/<session_id>?level=1
    """
    try:
        user_id = get_jwt_identity()
        hint_level = int(request.args.get('level', 1))
        
        # Validate hint level
        if hint_level not in [1, 2, 3]:
            return jsonify({'error': 'Hint level must be 1, 2, or 3'}), 400
        
        # Get session
        session = TranslationSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Generate hints
        coach = TranslationCoachService()
        hints = coach.generate_hints(
            questions=session.ai_questions,
            hint_level=hint_level
        )
        
        # Update hints count
        session.hints_requested += 1
        db.session.commit()
        
        return jsonify({
            'hints': hints,
            'hint_level': hint_level,
            'total_hints_used': session.hints_requested
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting hints: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@translation_bp.route('/practice', methods=['GET'])
@jwt_required()
def get_practice_sentence():
    """
    Get a practice sentence for translation.
    
    GET /api/translation/practice?target_language=es&difficulty=intermediate&grammar=past_tense
    """
    try:
        target_lang = request.args.get('target_language', 'es')
        difficulty = request.args.get('difficulty', 'intermediate')
        grammar_focus = request.args.get('grammar')
        
        # Validate language code
        if not validate_language_code(target_lang):
            return jsonify({'error': 'Invalid target language code'}), 400
        
        # Validate difficulty
        if difficulty not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Difficulty must be beginner, intermediate, or advanced'}), 400
        
        coach = TranslationCoachService()
        practice = coach.get_practice_sentence(
            target_lang=target_lang,
            difficulty=difficulty,
            grammar_focus=grammar_focus
        )
        
        return jsonify(practice), 200
        
    except Exception as e:
        logger.error(f"Error getting practice sentence: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@translation_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """
    Get user's translation learning progress.
    
    GET /api/translation/progress?language=es
    """
    try:
        user_id = get_jwt_identity()
        language = request.args.get('language')
        
        if language:
            # Get progress for specific language
            progress = UserProgress.query.filter_by(
                user_id=user_id,
                language=language
            ).first()
            
            if not progress:
                return jsonify({'error': 'No progress found for this language'}), 404
            
            return jsonify(progress.to_dict()), 200
        else:
            # Get progress for all languages
            all_progress = UserProgress.query.filter_by(user_id=user_id).all()
            return jsonify({
                'languages': [p.to_dict() for p in all_progress]
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@translation_bp.route('/history', methods=['GET'])
@jwt_required()
def get_translation_history():
    """
    Get user's translation session history.
    
    GET /api/translation/history?language=es&limit=20&offset=0
    """
    try:
        user_id = get_jwt_identity()
        language = request.args.get('language')
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = TranslationSession.query.filter_by(
            user_id=user_id,
            completed=True
        )
        
        if language:
            query = query.filter_by(target_language=language)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        sessions = query.order_by(
            TranslationSession.completed_at.desc()
        ).limit(limit).offset(offset).all()
        
        return jsonify({
            'sessions': [s.to_dict() for s in sessions],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
