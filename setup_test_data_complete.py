#!/usr/bin/env python3
"""
Complete Test Data Setup for Authorization System
This script ensures we have comprehensive test data for all 20 test cases
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

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
        print("🎯 SETTING UP COMPREHENSIVE TEST DATA")
        print("="*60)
        
        # Step 1: Ensure test users exist
        print("\n👥 Step 1: Setting up test users...")
        
        test_users = [
            {"userId": "testuser1", "password": "pass123"},
            {"userId": "testuser2", "password": "pass456"}, 
            {"userId": "ta_user", "password": "ta_pass"},
            {"userId": "student1", "password": "student123"},
            {"userId": "student2", "password": "student456"}
        ]
        
        users_added = 0
        for user in test_users:
            existing = users_col.find_one({"userId": user["userId"]})
            if not existing:
                users_col.insert_one(user)
                users_added += 1
                print(f"  ✅ Added user: {user['userId']}")
            else:
                print(f"  ⏭️  User already exists: {user['userId']}")
        
        print(f"📊 Test users added: {users_added}")
        
        # Step 2: Create test projects with different access patterns
        print("\n📋 Step 2: Setting up test projects...")
        
        test_projects = [
            {
                "projectId": "TEST-PUBLIC-001",
                "name": "Public Test Project 1", 
                "description": "Public project for testing cross-user access",
                "createdBy": "testuser1",
                "members": ["testuser1"],
                "isPublic": True
            },
            {
                "projectId": "TEST-PRIVATE-001",
                "name": "Private Test Project 1",
                "description": "Private project for testing access control", 
                "createdBy": "testuser1",
                "members": ["testuser1"],
                "isPublic": False
            },
            {
                "projectId": "TEST-SHARED-001", 
                "name": "Shared Test Project",
                "description": "Multi-user project for testing collaboration",
                "createdBy": "testuser1", 
                "members": ["testuser1", "testuser2", "ta_user"],
                "isPublic": False
            },
            {
                "projectId": "TA-PROJECT-001",
                "name": "TA Test Project",
                "description": "Project for TA testing scenarios",
                "createdBy": "ta_user",
                "members": ["ta_user"],
                "isPublic": True
            }
        ]
        
        projects_added = 0
        for project in test_projects:
            existing = projects_col.find_one({"projectId": project["projectId"]})
            if not existing:
                projects_col.insert_one(project)
                projects_added += 1
                print(f"  ✅ Added project: {project['projectId']} ({project['name']})")
                print(f"    Creator: {project['createdBy']}, Members: {project['members']}, Public: {project['isPublic']}")
            else:
                print(f"  ⏭️  Project already exists: {project['projectId']}")
        
        print(f"📊 Test projects added: {projects_added}")
        
        # Step 3: Add comprehensive hardware resources
        print("\n🔧 Step 3: Setting up hardware resources...")
        
        # Get all test projects
        test_project_ids = [p["projectId"] for p in test_projects]
        
        hardware_resources = []
        for project_id in test_project_ids:
            hardware_resources.extend([
                {
                    "projectId": project_id,
                    "hwsetId": "HWSet1",
                    "name": "Arduino Uno Kit",
                    "total": 15,
                    "allocatedToProject": 0,
                    "available": 15,
                    "notes": f"Arduino development kits for {project_id}"
                },
                {
                    "projectId": project_id,
                    "hwsetId": "HWSet2", 
                    "name": "Raspberry Pi Kit",
                    "total": 10,
                    "allocatedToProject": 0,
                    "available": 10,
                    "notes": f"Raspberry Pi development kits for {project_id}"
                }
            ])
        
        resources_added = 0
        for resource in hardware_resources:
            existing = resources_col.find_one({
                "projectId": resource["projectId"],
                "hwsetId": resource["hwsetId"]
            })
            if not existing:
                resources_col.insert_one(resource)
                resources_added += 1
                print(f"  ✅ Added: {resource['hwsetId']} to {resource['projectId']} (Total: {resource['total']})")
            else:
                print(f"  ⏭️  Resource already exists: {resource['hwsetId']} in {resource['projectId']}")
        
        print(f"📊 Hardware resources added: {resources_added}")
        
        # Step 4: Display test scenario mapping
        print("\n" + "="*60)
        print("🎯 TEST SCENARIO MAPPING")
        print("="*60)
        
        print("\n📋 Available Test Users:")
        all_users = list(users_col.find({}, {"_id": 0, "userId": 1}))
        for user in all_users:
            print(f"  - {user['userId']}")
        
        print(f"\n📋 Test Projects by Access Type:")
        all_projects = list(projects_col.find({}, {
            "_id": 0, "projectId": 1, "name": 1, "createdBy": 1, 
            "members": 1, "isPublic": 1
        }))
        
        public_projects = [p for p in all_projects if p.get("isPublic")]
        private_projects = [p for p in all_projects if not p.get("isPublic")]
        
        print(f"\n  🌐 Public Projects ({len(public_projects)}):")
        for project in public_projects:
            print(f"    - {project['projectId']}: {project['name']}")
            print(f"      Creator: {project['createdBy']}, Members: {project['members']}")
        
        print(f"\n  🔒 Private Projects ({len(private_projects)}):")
        for project in private_projects:
            print(f"    - {project['projectId']}: {project['name']}")
            print(f"      Creator: {project['createdBy']}, Members: {project['members']}")
        
        print(f"\n🔧 Hardware Resources by Project:")
        for project in test_project_ids:
            project_resources = list(resources_col.find(
                {"projectId": project},
                {"_id": 0, "hwsetId": 1, "name": 1, "total": 1, "available": 1}
            ))
            print(f"\n  📋 {project}:")
            for resource in project_resources:
                print(f"    - {resource['hwsetId']}: {resource['name']} (Available: {resource['available']}/{resource['total']})")
        
        # Step 5: Test case scenarios
        print(f"\n" + "="*60)
        print("🧪 TEST CASE SCENARIOS READY")
        print("="*60)
        
        scenarios = [
            "1-3: User Management - Use testuser1/testuser2 for signup/login testing",
            "4-6: Project Creation - Create new projects with different users", 
            "7-12: Hardware Checkout - Use TEST-PUBLIC-001 or TEST-SHARED-001",
            "13-15: Session Management - Test logout/login persistence",
            "16-17: Cross-user Access - TA can test with TA-PROJECT-001",
            "18-20: Multi-user Hardware - Test checkout/checkin across users in TEST-SHARED-001"
        ]
        
        for scenario in scenarios:
            print(f"  ✅ {scenario}")
        
        print(f"\n🎯 Database is fully prepared for all 20 test cases!")
        print(f"📊 Final counts:")
        print(f"  - Users: {users_col.count_documents({})}")
        print(f"  - Projects: {projects_col.count_documents({})}")
        print(f"  - Hardware Resources: {resources_col.count_documents({})}")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
