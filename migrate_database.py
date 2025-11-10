#!/usr/bin/env python3
"""
Database Migration Script for Authorization System
This script updates the existing MongoDB data to support the new authorization features
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def main():
    MONGODB_URI = os.getenv("MONGODB_URI")
    if not MONGODB_URI:
        print("❌ MONGODB_URI not found in environment variables")
        return
    
    try:
        # Connect to MongoDB
        print("🔗 Connecting to MongoDB...")
        client = MongoClient(MONGODB_URI)
        db = client["softwarelabdb"]
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get collections
        users_col = db.get_collection("Users")
        projects_col = db.get_collection("Projects")
        resources_col = db.get_collection("Resources")
        
        print("\n" + "="*60)
        print("🔄 MIGRATING DATABASE FOR AUTHORIZATION SYSTEM")
        print("="*60)
        
        # Step 1: Update Projects collection with authorization fields
        print("\n📋 Step 1: Updating Projects collection...")
        
        projects_updated = 0
        projects_cursor = projects_col.find({})
        
        for project in projects_cursor:
            project_id = project.get("projectId")
            updates = {}
            
            # Add createdBy field if missing (use a default or first user)
            if "createdBy" not in project:
                # Try to find a reasonable creator (first user in system, or create default)
                first_user = users_col.find_one({})
                if first_user:
                    updates["createdBy"] = first_user["userId"]
                else:
                    # Create a default admin user if no users exist
                    default_user = {"userId": "admin", "password": "admin123"}
                    users_col.insert_one(default_user)
                    updates["createdBy"] = "admin"
                    print(f"  ⚠️  Created default admin user for project {project_id}")
            
            # Add members field if missing (include creator)
            if "members" not in project:
                creator = updates.get("createdBy", project.get("createdBy", "admin"))
                updates["members"] = [creator]
            
            # Add isPublic field if missing (default to True for backward compatibility)
            if "isPublic" not in project:
                updates["isPublic"] = True  # Make existing projects public so they remain accessible
            
            # Apply updates if any
            if updates:
                projects_col.update_one(
                    {"_id": project["_id"]}, 
                    {"$set": updates}
                )
                projects_updated += 1
                print(f"  ✅ Updated project {project_id}: {list(updates.keys())}")
        
        print(f"📊 Projects updated: {projects_updated}")
        
        # Step 2: Ensure proper indexes exist
        print("\n📊 Step 2: Creating/updating database indexes...")
        
        # Users collection indexes
        try:
            users_col.create_index("userId", unique=True)
            print("  ✅ Users.userId index created/verified")
        except Exception as e:
            print(f"  ⚠️  Users.userId index already exists: {e}")
        
        # Projects collection indexes  
        try:
            projects_col.create_index("projectId", unique=True)
            print("  ✅ Projects.projectId index created/verified")
        except Exception as e:
            print(f"  ⚠️  Projects.projectId index already exists: {e}")
            
        try:
            projects_col.create_index("members")
            print("  ✅ Projects.members index created for fast member lookup")
        except Exception as e:
            print(f"  ⚠️  Projects.members index: {e}")
            
        try:
            projects_col.create_index("createdBy")
            print("  ✅ Projects.createdBy index created")
        except Exception as e:
            print(f"  ⚠️  Projects.createdBy index: {e}")
        
        # Resources collection indexes
        try:
            resources_col.create_index("projectId")
            print("  ✅ Resources.projectId index created/verified")
        except Exception as e:
            print(f"  ⚠️  Resources.projectId index: {e}")
            
        try:
            resources_col.create_index([("projectId", 1), ("hwsetId", 1)], unique=True)
            print("  ✅ Resources compound index (projectId, hwsetId) created")
        except Exception as e:
            print(f"  ⚠️  Resources compound index: {e}")
        
        # Step 3: Add sample hardware resources if none exist
        print("\n🔧 Step 3: Ensuring hardware resources exist...")
        
        resource_count = resources_col.count_documents({})
        if resource_count == 0:
            print("  ⚠️  No hardware resources found. Adding sample resources...")
            
            # Get all projects to add resources to
            all_projects = list(projects_col.find({}, {"projectId": 1}))
            
            sample_resources = []
            for project in all_projects[:3]:  # Add to first 3 projects
                project_id = project["projectId"]
                sample_resources.extend([
                    {
                        "projectId": project_id,
                        "hwsetId": "HWSet1",
                        "name": "Arduino Uno Kit",
                        "total": 10,
                        "allocatedToProject": 0,
                        "available": 10,
                        "notes": f"Arduino kits for {project_id}"
                    },
                    {
                        "projectId": project_id,
                        "hwsetId": "HWSet2", 
                        "name": "Raspberry Pi Kit",
                        "total": 5,
                        "allocatedToProject": 0,
                        "available": 5,
                        "notes": f"Raspberry Pi kits for {project_id}"
                    }
                ])
            
            if sample_resources:
                resources_col.insert_many(sample_resources)
                print(f"  ✅ Added {len(sample_resources)} sample hardware resources")
        else:
            print(f"  ✅ Hardware resources already exist ({resource_count} resources)")
        
        # Step 4: Verify data integrity
        print("\n🔍 Step 4: Verifying data integrity...")
        
        # Check all projects have required fields
        projects_missing_fields = list(projects_col.find({
            "$or": [
                {"createdBy": {"$exists": False}},
                {"members": {"$exists": False}}, 
                {"isPublic": {"$exists": False}}
            ]
        }))
        
        if projects_missing_fields:
            print(f"  ⚠️  {len(projects_missing_fields)} projects still missing authorization fields")
            for project in projects_missing_fields:
                print(f"    - {project.get('projectId', 'Unknown')}: missing {[k for k in ['createdBy', 'members', 'isPublic'] if k not in project]}")
        else:
            print("  ✅ All projects have required authorization fields")
        
        # Check for orphaned resources (resources without valid projects)
        all_project_ids = set(p["projectId"] for p in projects_col.find({}, {"projectId": 1}))
        resource_project_ids = set(r["projectId"] for r in resources_col.find({}, {"projectId": 1}))
        orphaned_resources = resource_project_ids - all_project_ids
        
        if orphaned_resources:
            print(f"  ⚠️  Found {len(orphaned_resources)} orphaned resource project IDs: {orphaned_resources}")
        else:
            print("  ✅ All resources belong to valid projects")
        
        # Step 5: Display final state
        print("\n" + "="*60)
        print("📈 MIGRATION SUMMARY")
        print("="*60)
        
        user_count = users_col.count_documents({})
        project_count = projects_col.count_documents({})
        resource_count = resources_col.count_documents({})
        
        print(f"👥 Users: {user_count}")
        print(f"📋 Projects: {project_count}")
        print(f"🔧 Hardware Resources: {resource_count}")
        
        # Show sample of updated projects
        print(f"\n📋 Sample Projects (showing authorization fields):")
        sample_projects = list(projects_col.find({}, {
            "_id": 0, "projectId": 1, "name": 1, "createdBy": 1, 
            "members": 1, "isPublic": 1
        }).limit(3))
        
        for project in sample_projects:
            print(f"  - {project['projectId']}: {project['name']}")
            print(f"    Creator: {project.get('createdBy', 'Unknown')}")
            print(f"    Members: {project.get('members', [])}")
            print(f"    Public: {project.get('isPublic', False)}")
        
        print(f"\n🎯 Database migration completed successfully!")
        print(f"✅ Authorization system is ready for testing!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
