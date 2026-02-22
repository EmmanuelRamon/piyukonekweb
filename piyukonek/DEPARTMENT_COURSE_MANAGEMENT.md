# Department and Course Management System

## Overview
The PIYUKONEK system now includes comprehensive department and course management functionality for administrators. This feature allows admins to add, edit, archive, and restore college departments and their associated courses.

## Features

### Department Management
- ✅ **Add Departments**: Create new college departments with name, code, and description
- ✅ **Edit Departments**: Update department information
- ✅ **Archive Departments**: Archive departments (also archives all associated courses)
- ✅ **Restore Departments**: Restore archived departments
- ✅ **Search & Filter**: Search departments by name, code, or description
- ✅ **Status Filtering**: Filter by active or archived departments
- ✅ **Course Statistics**: View active and total course counts per department

### Course Management
- ✅ **Add Courses**: Create new courses within departments
- ✅ **Edit Courses**: Update course information and department assignment
- ✅ **Archive Courses**: Archive individual courses
- ✅ **Restore Courses**: Restore archived courses (requires active department)
- ✅ **Search & Filter**: Search courses by name, code, department, or description
- ✅ **Department Filtering**: Filter courses by specific departments
- ✅ **Status Filtering**: Filter by active or archived courses

## Database Schema

### Departments Table
```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES admin (id)
);
```

### Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    description TEXT,
    department_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (created_by) REFERENCES admin (id),
    UNIQUE (code, department_id)
);
```

## API Endpoints

### Department Management Routes
- `GET /admin/departments` - View departments page
- `POST /admin/departments/add` - Add new department
- `POST /admin/departments/<id>/update` - Update department
- `POST /admin/departments/<id>/archive` - Archive department
- `POST /admin/departments/<id>/restore` - Restore department

### Course Management Routes
- `GET /admin/courses` - View courses page
- `POST /admin/courses/add` - Add new course
- `POST /admin/courses/<id>/update` - Update course
- `POST /admin/courses/<id>/archive` - Archive course
- `POST /admin/courses/<id>/restore` - Restore course

## Installation & Setup

### 1. Database Migration
Run the migration script to create the new tables:

```bash
cd /path/to/piyukonek
python create_department_course_tables.py
```

This will:
- Create the `departments` and `courses` tables
- Add sample data if tables are empty
- Verify the setup is working correctly

### 2. Navigation Update
The admin dashboard navigation has been updated to include:
- **Departments** - Manage college departments
- **Courses** - Manage courses within departments

### 3. Access Control
- Only admin users can access department and course management
- All routes are protected with `@login_required('admin')`
- Created by tracking for audit purposes

## Usage Guide

### Managing Departments

#### Adding a Department
1. Go to **Admin Dashboard** → **Departments**
2. Click **"Add Department"** button
3. Fill in the required information:
   - **Department Name**: Full name (e.g., "College of Computer Studies")
   - **Department Code**: Short code (e.g., "CCS")
   - **Description**: Optional description
4. Click **"Add Department"**

#### Editing a Department
1. Find the department in the list
2. Click **"Edit"** button on the department card
3. Update the information
4. Click **"Update Department"**

#### Archiving a Department
1. Find the active department
2. Click **"Archive"** button
3. Confirm the action
4. **Note**: This will also archive all courses in the department

#### Restoring a Department
1. Filter by "Archived Only" or "All Departments"
2. Find the archived department
3. Click **"Restore"** button
4. Confirm the action

### Managing Courses

#### Adding a Course
1. Go to **Admin Dashboard** → **Courses**
2. Click **"Add Course"** button
3. Fill in the required information:
   - **Course Name**: Full name (e.g., "Bachelor of Science in Computer Science")
   - **Course Code**: Short code (e.g., "BSCS")
   - **Department**: Select from active departments
   - **Description**: Optional description
4. Click **"Add Course"**

#### Editing a Course
1. Find the course in the table
2. Click **"Edit"** button
3. Update the information (including department if needed)
4. Click **"Update Course"**

#### Archiving a Course
1. Find the active course
2. Click **"Archive"** button
3. Confirm the action

#### Restoring a Course
1. Filter by "Archived Only" or "All Courses"
2. Find the archived course
3. Click **"Restore"** button
4. **Note**: The department must be active to restore a course

## Business Rules

### Department Rules
1. **Unique Names**: Department names must be unique across the system
2. **Unique Codes**: Department codes must be unique across the system
3. **Cascade Archive**: Archiving a department archives all its courses
4. **No Cascade Restore**: Restoring a department does not automatically restore courses

### Course Rules
1. **Unique Codes per Department**: Course codes must be unique within each department
2. **Active Department Required**: Courses can only be added to active departments
3. **Restore Dependency**: Archived courses can only be restored if their department is active
4. **Department Transfer**: Courses can be moved between departments via editing

## Sample Data

The system includes sample data for common Philippine university departments:

### Departments
- **College of Computer Studies (CCS)**
- **College of Engineering (COE)**
- **College of Business Administration (CBA)**
- **College of Education (COED)**
- **College of Arts and Sciences (CAS)**

### Sample Courses
- **CCS**: BSCS, BSIT, BSIS
- **COE**: BSCE, BSEE
- **CBA**: BSBA, BSA
- **COED**: BEED, BSED
- **CAS**: AB-PSYC, BS-BIO

## Mobile Responsiveness

Both department and course management pages are fully responsive:
- **Mobile Navigation**: Hamburger menu for mobile devices
- **Responsive Tables**: Horizontal scrolling for course tables on mobile
- **Touch-Friendly**: All buttons and interactions optimized for touch
- **Modal Forms**: Mobile-optimized modal dialogs for adding/editing

## Security Features

- **Authentication Required**: All routes require admin authentication
- **Input Validation**: Server-side validation for all form inputs
- **SQL Injection Protection**: Parameterized queries and ORM usage
- **XSS Protection**: Proper input sanitization and output encoding
- **Audit Trail**: Created by tracking for all records

## Error Handling

- **Duplicate Prevention**: Checks for duplicate names and codes
- **Relationship Validation**: Ensures department exists before adding courses
- **Graceful Failures**: User-friendly error messages
- **Transaction Safety**: Database rollback on errors

## Future Enhancements

Potential future improvements:
1. **Bulk Operations**: Bulk archive/restore multiple items
2. **Import/Export**: CSV import/export functionality
3. **History Tracking**: Full audit log of changes
4. **Advanced Search**: More sophisticated search and filtering
5. **Department Hierarchy**: Support for sub-departments
6. **Course Prerequisites**: Course dependency management
7. **Academic Year Management**: Time-based course offerings

## Troubleshooting

### Common Issues

1. **Tables Not Created**
   - Run the migration script: `python create_department_course_tables.py`
   - Check database permissions

2. **Navigation Links Missing**
   - Clear browser cache
   - Verify admin user is logged in

3. **Sample Data Not Added**
   - Ensure admin user with ID 1 exists
   - Run migration script again

4. **Permission Errors**
   - Verify user has admin role
   - Check session authentication

### Database Verification
```python
# Check if tables exist
from app import app, db
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print("Departments table exists:", 'departments' in tables)
    print("Courses table exists:", 'courses' in tables)
```

## Support

For technical support or questions:
1. Check this documentation
2. Verify database setup with migration script
3. Check browser console for JavaScript errors
4. Ensure proper admin authentication

---

*Last updated: [Current Date]*
*Version: 1.0*
