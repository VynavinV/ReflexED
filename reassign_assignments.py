import os
from app import create_app, db
from app.models.models import Assignment

def reassign_assignments():
    """
    This script reassigns all assignments to the 'demo-teacher' user.
    This is useful for the hackathon demo to ensure all created assignments
    are visible to the default user.
    """
    app = create_app()

    with app.app_context():
        print("Querying all assignments...")
        assignments = Assignment.query.all()
        
        if not assignments:
            print("No assignments found in the database.")
            return

        print(f"Found {len(assignments)} assignments. Reassigning to 'demo-teacher' where necessary.")
        
        updated_count = 0
        for assignment in assignments:
            if assignment.teacher_id != 'demo-teacher':
                print(f"  - Updating assignment '{assignment.title}' (ID: {assignment.id}) from teacher '{assignment.teacher_id}' to 'demo-teacher'")
                assignment.teacher_id = 'demo-teacher'
                updated_count += 1

        if updated_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully updated {updated_count} assignments.")
        else:
            print("\n✅ All assignments are already assigned to 'demo-teacher'. No updates needed.")

        print("\nVerifying all assignments now belong to 'demo-teacher':")
        assignments_after = Assignment.query.all()
        all_correct = True
        for a in assignments_after:
            print(f"  - '{a.title}' -> Teacher: {a.teacher_id}")
            if a.teacher_id != 'demo-teacher':
                all_correct = False
        
        if all_correct:
            print("\nVerification successful!")
        else:
            print("\nVerification failed. Some assignments still have incorrect ownership.")

if __name__ == '__main__':
    reassign_assignments()
