# MongoDB Data Structure Documentation

## Database: `softwarelabdb`

This document outlines the MongoDB collections and their data structures used in the HaaS (Hardware-as-a-Service) application.

## Collections Overview

### 1. Users Collection
**Collection Name:** `Users`
**Purpose:** Store user authentication data

```json
{
  "_id": ObjectId("..."),
  "userId": "string (unique)",
  "password": "string (plaintext - demo only)"
}
```

**Indexes:**
- `userId` (unique)

**Example Document:**
```json
{
  "_id": ObjectId("673123456789abcdef123456"),
  "userId": "john_doe",
  "password": "mypassword123"
}
```

### 2. Projects Collection
**Collection Name:** `Projects`
**Purpose:** Store project information with user access control

```json
{
  "_id": ObjectId("..."),
  "projectId": "string (unique)",
  "name": "string",
  "description": "string",
  "createdAt": "date or null",
  "createdBy": "string (userId of project creator)",
  "members": ["array of userIds with access to this project"],
  "isPublic": "boolean (if true, anyone can join)"
}
```

**Indexes:**
- `projectId` (unique)

**Example Documents:**
```json
[
  {
    "_id": ObjectId("673123456789abcdef123457"),
    "projectId": "P-001",
    "name": "Project A",
    "description": "Example project",
    "createdAt": "Mon, 27 Oct 2025 00:00:00 GMT",
    "createdBy": "john_doe",
    "members": ["john_doe", "jane_smith"],
    "isPublic": false
  },
  {
    "_id": ObjectId("673123456789abcdef123458"),
    "projectId": "P-002",
    "name": "Project B", 
    "description": "Example project",
    "createdAt": "Mon, 27 Oct 2025 00:00:00 GMT",
    "createdBy": "alice_wilson",
    "members": ["alice_wilson"],
    "isPublic": true
  }
]
```

### 3. Resources Collection
**Collection Name:** `Resources`
**Purpose:** Store hardware resource information and allocation

```json
{
  "_id": ObjectId("..."),
  "projectId": "string (references Projects.projectId)",
  "hwsetId": "string (hardware set identifier)",
  "name": "string (human-readable name)",
  "total": "number (total units available)",
  "allocatedToProject": "number (units checked out)",
  "available": "number (units available for checkout)",
  "notes": "string (optional notes)"
}
```

**Indexes:**
- `projectId` (for fast lookup by project)

**Example Documents:**
```json
[
  {
    "_id": ObjectId("673123456789abcdef123459"),
    "projectId": "P-001",
    "hwsetId": "HWSet1",
    "name": "Arduino Uno Kit",
    "total": 10,
    "allocatedToProject": 3,
    "available": 7,
    "notes": "Includes breadboard and jumper wires"
  },
  {
    "_id": ObjectId("673123456789abcdef12345a"),
    "projectId": "P-001", 
    "hwsetId": "HWSet2",
    "name": "Raspberry Pi Kit",
    "total": 5,
    "allocatedToProject": 1,
    "available": 4,
    "notes": "Includes SD card and power adapter"
  }
]
```

## API Integration Points

### Authentication Endpoints
- `POST /api/signup` → Creates document in `Users` collection
- `POST /api/login` → Validates against `Users` collection

### Project Endpoints  
- `GET /api/projects` → Reads from `Projects` collection
- `GET /api/projects/{id}` → Reads specific document from `Projects` collection
- `POST /api/projects` → Creates document in `Projects` collection

### Hardware Resource Endpoints
- `GET /api/projects/{id}/resources` → Reads from `Resources` collection filtered by projectId
- `POST /api/projects/{id}/resources/{hwsetId}/checkout` → Updates `Resources` collection (decreases available, increases allocated)
- `POST /api/projects/{id}/resources/{hwsetId}/checkin` → Updates `Resources` collection (increases available, decreases allocated)

## Data Flow Examples

### User Signup Flow
1. Frontend sends POST to `/api/signup` with `{userId, password}`
2. Backend validates input
3. Backend inserts new document into `Users` collection
4. Returns success or duplicate error

### Hardware Checkout Flow
1. Frontend sends POST to `/api/projects/P-001/resources/HWSet1/checkout` with `{quantity: 2, userId: "john_doe"}`
2. Backend finds resource document where `projectId="P-001"` and `hwsetId="HWSet1"`
3. Backend validates availability (available >= quantity)
4. Backend updates document: `available -= 2`, `allocatedToProject += 2`
5. Returns updated quantities

### Project Creation Flow
1. Frontend sends POST to `/api/projects` with `{projectId, name, description}`
2. Backend validates input and uniqueness
3. Backend inserts new document into `Projects` collection
4. Returns success or duplicate error

## Current Database State (Based on API Response)

From the `/api/projects` endpoint, we can see these existing projects:

```json
[
  {"projectId": "P-001", "name": "Project A", "description": "Example project"},
  {"projectId": "P-002", "name": "Project B", "description": "Example project"}, 
  {"projectId": "P-003", "name": "Project C", "description": "Created via API"},
  {"projectId": "P-004", "name": "UI", "description": "created from ui"},
  {"projectId": "P-005", "name": "project 5", "description": "new project in demo"},
  {"projectId": "P-009", "name": "sid", "description": "monkey"},
  {"projectId": "P-101", "name": "sid2", "description": "monkey"},
  {"projectId": "p-009", "name": "p-009", "description": "abc"},
  {"projectId": "p-001111", "name": "test", "description": "testing the "},
  {"projectId": "P-01234", "name": "Ashwin", "description": "Testing functionality"}
]
```

## MongoDB Connection Details

- **Connection URI:** Set via `MONGODB_URI` environment variable
- **Database Name:** `softwarelabdb`
- **Driver:** PyMongo (Python MongoDB driver)
- **Connection Pool:** Managed automatically by PyMongo

## Data Validation Rules

### Users Collection
- `userId`: Required, unique, string
- `password`: Required, string

### Projects Collection  
- `projectId`: Required, unique, string
- `name`: Required, string
- `description`: Optional, string, defaults to ""
- `createdAt`: Optional, date

### Resources Collection
- `projectId`: Required, string (must reference existing project)
- `hwsetId`: Required, string
- `name`: Required, string
- `total`: Required, positive integer
- `allocatedToProject`: Required, non-negative integer, <= total
- `available`: Required, non-negative integer, <= total
- `notes`: Optional, string

## Constraints and Business Rules

1. **Hardware Allocation:** `allocatedToProject + available <= total`
2. **Checkout Validation:** Cannot checkout more than `available`
3. **Checkin Validation:** Cannot checkin more than `allocatedToProject`
4. **User Authentication:** All hardware operations require valid `userId`
5. **Project Access:** Users can access any project (no ownership restrictions in current implementation)

## Testing Data Requirements

For the 20 test cases, ensure MongoDB has:

1. **Hardware Resources:** At least 2 different hardware sets (HWSet1, HWSet2) with sufficient quantities
2. **Test Projects:** Projects that can be joined by different users
3. **User Accounts:** Multiple test user accounts for cross-user testing

## Sample Test Data Setup

```javascript
// Users for testing
db.Users.insertMany([
  {userId: "testuser1", password: "pass123"},
  {userId: "testuser2", password: "pass456"},
  {userId: "ta_user", password: "ta_pass"}
]);

// Projects for testing  
db.Projects.insertMany([
  {projectId: "TEST-001", name: "Test Project 1", description: "For testing hardware checkout"},
  {projectId: "TEST-002", name: "Test Project 2", description: "For testing project joining"}
]);

// Hardware resources for testing
db.Resources.insertMany([
  {
    projectId: "TEST-001",
    hwsetId: "HWSet1", 
    name: "Arduino Kit",
    total: 10,
    allocatedToProject: 0,
    available: 10,
    notes: "For testing checkout/checkin"
  },
  {
    projectId: "TEST-001",
    hwsetId: "HWSet2",
    name: "Raspberry Pi Kit", 
    total: 5,
    allocatedToProject: 0,
    available: 5,
    notes: "For testing checkout/checkin"
  }
]);
```
