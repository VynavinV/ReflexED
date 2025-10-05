import os
import uuid
import json
from datetime import datetime
from app import create_app, db
from app.models.models import Assignment, AssignmentVersion

def recover_assignments():
    """
    Scans the uploads directory for orphaned assignment folders and recreates
    their database entries.
    """
    app = create_app()
    with app.app_context():
        upload_root = os.path.abspath('uploads')
        if not os.path.exists(upload_root):
            print(f"Uploads directory not found at: {upload_root}")
            return

        print("Scanning for orphaned assignments...")
        
        existing_ids = {str(a.id) for a in Assignment.query.with_entities(Assignment.id).all()}
        print(f"Found {len(existing_ids)} existing assignments in the database.")

        recovered_count = 0
        for dir_name in os.listdir(upload_root):
            dir_path = os.path.join(upload_root, dir_name)
            if not os.path.isdir(dir_path):
                continue

            try:
                # Check if directory name is a valid UUID
                uuid.UUID(dir_name)
            except ValueError:
                continue

            if dir_name in existing_ids:
                print(f"Skipping '{dir_name}', already in database.")
                continue

            print(f"Found orphaned assignment: {dir_name}. Attempting recovery...")
            
            # Attempt to get metadata from quiz.json
            quiz_path = os.path.join(dir_path, 'quiz.json')
            title = f"Recovered Assignment {dir_name[:8]}"
            subject = "unknown"

            if os.path.exists(quiz_path):
                try:
                    with open(quiz_path, 'r') as f:
                        quiz_data = json.load(f)
                    # Try to infer subject from quiz type or summary
                    if 'quiz_type' in quiz_data:
                        if quiz_data['quiz_type'] == 'practice':
                            subject = 'math'
                        elif quiz_data['quiz_type'] == 'socratic':
                            subject = 'language'
                    title = quiz_data.get('summary', title)
                except (json.JSONDecodeError, KeyError):
                    print(f"  - Could not parse quiz.json for metadata.")
            
            new_assignment = Assignment(
                id=dir_name,
                title=title,
                subject=subject,
                teacher_id='demo-teacher',
                status='ready',
                created_at=datetime.fromtimestamp(os.path.getctime(dir_path))
            )
            db.session.add(new_assignment)
            
            # Also create dummy versions so they appear correctly
            variant_map = {
                'simplified': 'simplified.json',
                'audio': 'podcast.mp3',
                'visual': 'visual.mp4',
                'quiz': 'quiz.json'
            }
            for variant_type, asset_name in variant_map.items():
                if os.path.exists(os.path.join(dir_path, asset_name)):
                    version = AssignmentVersion(
                        assignment_id=dir_name,
                        variant_type=variant_type,
                        subject=new_assignment.subject,
                        ready=True,
                        content_text='{"recovered": true}',
                        assets=f'{{"{variant_type}_asset": "{asset_name}"}}'
                    )
                    db.session.add(version)

            recovered_count += 1
            print(f"  - Successfully created database entry for {dir_name}")

        if recovered_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully recovered {recovered_count} assignments.")
        else:
            print("\nNo orphaned assignments found to recover.")

if __name__ == '__main__':
    recover_assignments()
