"""
Assignment API endpoints for creating and fetching teacher-generated lessons.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.models import Assignment, AssignmentVersion, User
from app.services.assignment_service import AssignmentService
import os

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')


@assignments_bp.route('', methods=['GET'])
def list_assignments():
    """List assignments (all for now; hackathon demo)."""
    rows = Assignment.query.order_by(Assignment.created_at.desc()).all()
    return jsonify([a.to_dict(include_versions=False) for a in rows]), 200


@assignments_bp.route('/<assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    return jsonify(a.to_dict(include_versions=True)), 200


@assignments_bp.route('/student', methods=['GET'])
def list_for_student():
    """Student view: return ready assignments with basic metadata and available variants."""
    rows = Assignment.query.filter_by(status='ready').order_by(Assignment.created_at.desc()).all()
    payload = []
    for a in rows:
        variants = a.versions.all()
        payload.append({
            **a.to_dict(include_versions=False),
            'variant_types': [v.variant_type for v in variants if v.ready],
        })
    return jsonify(payload), 200


@assignments_bp.route('/create', methods=['POST'])
def create_assignment():
    """Create assignment from text or uploaded file and generate variants."""
    # For demo, use a default teacher ID if no JWT
    user_id = 'demo-teacher'
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity() or 'demo-teacher'
    except:
        pass

    title = request.form.get('title') or (request.json.get('title') if request.is_json else None)
    subject = request.form.get('subject') or (request.json.get('subject') if request.is_json else None)
    original_text = request.form.get('text') or (request.json.get('text') if request.is_json else None)

    print(f"DEBUG: title={title}, subject={subject}, has_file={'file' in request.files}, text={original_text[:50] if original_text else None}")
    
    if not title or not subject:
        return jsonify({'error': f'title and subject are required (got title={title}, subject={subject})'}), 400

    # Validate that at least file or text is provided
    has_file = 'file' in request.files and request.files['file'].filename
    has_text = original_text and original_text.strip()
    
    if not has_file and not has_text:
        return jsonify({'error': 'Please provide either a file or lesson text (or both)'}), 400

    # Handle file upload (optional)
    file_path = None
    if 'file' in request.files:
        f = request.files['file']
        if f and f.filename:
            upload_root = os.path.abspath('uploads')
            os.makedirs(upload_root, exist_ok=True)
            safe_name = f"{user_id}_{a_slug(title)}_{f.filename}"
            file_path = os.path.join(upload_root, safe_name)
            f.save(file_path)

    try:
        svc = AssignmentService()
        assignment = svc.create_assignment(
            title=title,
            subject=subject,
            teacher_id=user_id,
            original_text=original_text,
            file_path=file_path,
        )
        return jsonify(assignment.to_dict(include_versions=True)), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignments_bp.route('/<assignment_id>/regenerate/quiz', methods=['POST'])
def regenerate_quiz(assignment_id):
    """Regenerate the quiz variant for an assignment with adjusted difficulty."""
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Get difficulty from request (optional)
        data = request.get_json() or {}
        difficulty = data.get('difficulty', 'medium')  # easy, medium, hard
        
        # Regenerate quiz variant
        svc = AssignmentService()
        quiz_version = svc.regenerate_variant(
            assignment=assignment,
            variant_type='quiz',
            difficulty=difficulty
        )
        
        return jsonify({
            'success': True,
            'message': 'Quiz regenerated successfully',
            'quiz': quiz_version.to_dict()
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def a_slug(text: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '-' for c in text)[:80]
