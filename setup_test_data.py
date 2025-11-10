#!/usr/bin/env python3
"""
Setup Test Data for MongoDB
This script adds additional test hardware resources to ensure comprehensive testing
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
        
        resources_col = db.get_collection("Resources")
        
        # Check existing resources
        existing_count = resources_col.count_documents({})
        print(f"📊 Current hardware resources: {existing_count}")
        
        # Additional test hardware resources
        additional_resources = [
            {
                "projectId": "P-001",
                "hwsetId": "HWSet1", 
                "name": "Arduino Uno Kit",
                "total": 15,
                "allocatedToProject": 0,
                "available": 15,
                "notes": "Complete Arduino starter kit with sensors"
            },
            {
                "projectId": "P-001",
                "hwsetId": "HWSet2",
                "name": "Raspberry Pi Kit", 
                "total": 8,
                "allocatedToProject": 0,
                "available": 8,
                "notes": "Raspberry Pi 4 with accessories"
            },
            {
                "projectId": "P-002",
                "hwsetId": "HWSet1",
                "name": "Arduino Uno Kit",
                "total": 12,
                "allocatedToProject": 0, 
                "available": 12,
                "notes": "Arduino kits for Project B"
            },
            {
                "projectId": "P-002", 
                "hwsetId": "HWSet2",
                "name": "Raspberry Pi Kit",
                "total": 6,
                "allocatedToProject": 0,
                "available": 6,
                "notes": "Pi kits for Project B"
            },
            {
                "projectId": "P-003",
                "hwsetId": "HWSet1", 
                "name": "Arduino Uno Kit",
                "total": 10,
                "allocatedToProject": 0,
                "available": 10,
                "notes": "Arduino kits for Project C"
            },
            {
                "projectId": "P-003",
                "hwsetId": "HWSet2",
                "name": "Raspberry Pi Kit",
                "total": 5,
                "allocatedToProject": 0,
                "available": 5,
                "notes": "Pi kits for Project C"
            }
        ]
        
        # Check which resources already exist and add only new ones
        added_count = 0
        for resource in additional_resources:
            existing = resources_col.find_one({
                "projectId": resource["projectId"],
                "hwsetId": resource["hwsetId"]
            })
            
            if not existing:
                resources_col.insert_one(resource)
                added_count += 1
                print(f"✅ Added: {resource['name']} for {resource['projectId']}")
            else:
                print(f"⏭️  Skipped: {resource['name']} for {resource['projectId']} (already exists)")
        
        print(f"\n📈 Summary:")
        print(f"  - Resources before: {existing_count}")
        print(f"  - Resources added: {added_count}")
        print(f"  - Total resources now: {resources_col.count_documents({})}")
        
        # Show final state
        print(f"\n🔧 Final Hardware Resources by Project:")
        projects = resources_col.distinct("projectId")
        for project_id in sorted(projects):
            project_resources = list(resources_col.find(
                {"projectId": project_id}, 
                {"_id": 0, "hwsetId": 1, "name": 1, "total": 1, "available": 1}
            ))
            print(f"\n  📋 {project_id}:")
            for res in project_resources:
                print(f"    - {res['hwsetId']}: {res['name']} (Total: {res['total']}, Available: {res['available']})")
        
        print(f"\n🎯 MongoDB is now ready for all 20 test cases!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
