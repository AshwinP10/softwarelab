#!/usr/bin/env python3
"""
MongoDB Integration Verification Script
This script connects to MongoDB and displays the current data structure
"""

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Get MongoDB URI
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
        collections = db.list_collection_names()
        print(f"\n📁 Available collections: {collections}")
        
        # Analyze Users collection
        print("\n" + "="*50)
        print("👥 USERS COLLECTION")
        print("="*50)
        users_col = db.get_collection("Users")
        user_count = users_col.count_documents({})
        print(f"Total users: {user_count}")
        
        if user_count > 0:
            print("\nSample users:")
            for user in users_col.find({}, {"_id": 0}).limit(5):
                # Hide password for security
                user_display = {k: v if k != 'password' else '***' for k, v in user.items()}
                print(f"  - {json.dumps(user_display, indent=4)}")
        
        # Analyze Projects collection
        print("\n" + "="*50)
        print("📋 PROJECTS COLLECTION")
        print("="*50)
        projects_col = db.get_collection("Projects")
        project_count = projects_col.count_documents({})
        print(f"Total projects: {project_count}")
        
        if project_count > 0:
            print("\nAll projects:")
            for project in projects_col.find({}, {"_id": 0}):
                print(f"  - {json.dumps(project, indent=4, default=str)}")
        
        # Analyze Resources collection
        print("\n" + "="*50)
        print("🔧 RESOURCES COLLECTION")
        print("="*50)
        resources_col = db.get_collection("Resources")
        resource_count = resources_col.count_documents({})
        print(f"Total hardware resources: {resource_count}")
        
        if resource_count > 0:
            print("\nAll hardware resources:")
            for resource in resources_col.find({}, {"_id": 0}):
                print(f"  - {json.dumps(resource, indent=4, default=str)}")
        else:
            print("\n⚠️  No hardware resources found!")
            print("You may need to add some test hardware resources for testing.")
            print("\nSample hardware resources you can add:")
            sample_resources = [
                {
                    "projectId": "P-001",
                    "hwsetId": "HWSet1",
                    "name": "Arduino Uno Kit",
                    "total": 10,
                    "allocatedToProject": 0,
                    "available": 10,
                    "notes": "Includes breadboard and jumper wires"
                },
                {
                    "projectId": "P-001", 
                    "hwsetId": "HWSet2",
                    "name": "Raspberry Pi Kit",
                    "total": 5,
                    "allocatedToProject": 0,
                    "available": 5,
                    "notes": "Includes SD card and power adapter"
                }
            ]
            for sample in sample_resources:
                print(f"  {json.dumps(sample, indent=2)}")
        
        # Check indexes
        print("\n" + "="*50)
        print("📊 COLLECTION INDEXES")
        print("="*50)
        
        print("Users collection indexes:")
        for index in users_col.list_indexes():
            print(f"  - {index}")
            
        print("\nProjects collection indexes:")
        for index in projects_col.list_indexes():
            print(f"  - {index}")
            
        print("\nResources collection indexes:")
        for index in resources_col.list_indexes():
            print(f"  - {index}")
        
        # Summary
        print("\n" + "="*50)
        print("📈 INTEGRATION SUMMARY")
        print("="*50)
        print(f"✅ MongoDB connection: Working")
        print(f"✅ Database 'softwarelabdb': Accessible")
        print(f"✅ Users collection: {user_count} documents")
        print(f"✅ Projects collection: {project_count} documents")
        print(f"✅ Resources collection: {resource_count} documents")
        
        if resource_count == 0:
            print(f"⚠️  Hardware resources: None found - add test data for hardware testing")
        else:
            print(f"✅ Hardware resources: Ready for testing")
            
        print(f"\n🎯 Ready for all 20 test cases!")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return

if __name__ == "__main__":
    main()
