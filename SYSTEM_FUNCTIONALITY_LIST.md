# PIYUKONEK System - Complete Functionality List

## System Overview
PIYUKONEK is a Student Concern Management System for Laguna State Polytechnic University - Sta. Cruz Campus, designed to facilitate communication and resolution of student concerns between students, SSC (Student Services Center/Guidance) staff, and administrators.

---

## 1. AUTHENTICATION & USER MANAGEMENT

### 1.1 Account Registration
- **Student Signup**
  - Registration with full name, username, student ID number
  - Email address verification
  - Course, college department, and year level selection
  - Certificate of Registration upload
  - Student ID image upload
  - OTP (One-Time Password) email verification
  - OTP resend functionality
  - Account status: pending approval by admin

- **SSC Staff Signup**
  - Registration with full name, username, email
  - Position specification
  - OTP email verification
  - OTP resend functionality
  - Account status: pending approval by admin

- **Admin Signup**
  - Registration with full name, username, email
  - OTP email verification
  - OTP resend functionality
  - Account status: pending approval by admin

### 1.2 Authentication
- Multi-role login system (Student, SSC, Admin)
- Secure password hashing (Werkzeug security)
- Session management with 30-minute timeout
- Session activity tracking
- Automatic session expiration handling
- Account status verification (active/pending)

### 1.3 Password Management
- Forgot password functionality
- Password reset via email token
- Secure token-based password reset links
- Token expiration handling

### 1.4 Account Type Selection
- Account type selection page for registration

---

## 2. STUDENT FUNCTIONALITIES

### 2.1 Dashboard
- Student dashboard with overview
- Quick access to concerns and notifications
- Profile information display

### 2.2 Concern Management
- **Create Concern**
  - Submit concerns with title and description
  - Select concern type (academic, financial, administrative, personal, other)
  - Set priority level (low, medium, high, urgent)
  - Upload multiple file attachments
  - File type and size validation
  - Automatic deadline setting (3 days from submission)

- **View Concerns**
  - View all submitted concerns
  - Filter by status (pending, processing, resolved, closed)
  - View concern details and attachments
  - Track concern timeline/history

- **Edit Concerns**
  - Edit concern details before processing
  - Update attachments
  - Remove attachments

- **Concern Timeline**
  - View detailed timeline of concern status changes
  - Download timeline as PDF

- **Rate & Feedback**
  - Rate resolved concerns (1-5 stars)
  - Provide feedback on guidance response
  - Submit feedback for resolved concerns

- **Attachment Management**
  - Upload multiple attachments per concern
  - View attachment details
  - Download attachments
  - Remove attachments

- **Export Functionality**
  - Export personal concern history as PDF
  - Export individual concern details as PDF
  - Detailed reports with statistics

### 2.3 Messaging System
- Real-time messaging with SSC staff and Admin
- Send messages related to specific concerns
- File attachments in messages
- View conversation history
- Delete conversations

### 2.4 Notifications
- View all notifications
- Mark individual notifications as read
- Mark all notifications as read
- Delete individual notifications
- Delete all notifications
- Notification types: concern updates, system notifications, reminders

### 2.5 Profile Management
- View and edit profile information
- Update personal details
- Upload profile image
- Change password

### 2.6 Reminders
- View concern reminders
- Automatic reminders for unresolved concerns (3-day and 5-day reminders)

### 2.7 AI Chatbot
- AI-powered concern analysis using Hugging Face API
- Get helpful advice for student concerns
- Interactive chatbot interface

---

## 3. SSC (STUDENT SERVICES CENTER) STAFF FUNCTIONALITIES

### 3.1 Dashboard
- SSC dashboard with overview statistics
- Quick access to pending concerns
- Staff activity overview
- Online/offline status tracking

### 3.2 Concern Management
- **View Concerns**
  - View all student concerns
  - Filter by status, type, priority, assigned staff
  - Search concerns
  - Sort by various criteria

- **Concern Details**
  - View detailed concern information
  - View student information
  - View all attachments
  - View concern timeline/history

- **Process Concerns**
  - Respond to concerns with detailed notes
  - Upload response attachments
  - Update response notes
  - Resolve concerns with resolution notes
  - Assign concerns to specific staff members
  - Change concern status (pending, processing, resolved, closed)

- **Bulk Operations**
  - Bulk update concern status
  - Bulk assign concerns to staff
  - Bulk export concerns to CSV
  - Bulk delete concerns

- **Staff Assignment**
  - View list of available SSC staff
  - Assign concerns to specific staff members
  - View concerns by assigned staff

- **Export Functionality**
  - Export concerns to CSV
  - Export students list to CSV
  - Export individual concern as PDF
  - Export analytics reports

### 3.3 Student Management
- View all students
- View student details
- View student concern history
- Student search and filter

### 3.4 Concern Type Management
- View all concern types
- Add new concern types
- Update existing concern types
- Archive/restore concern types

### 3.5 Messaging System
- Send messages to students
- Receive messages from students
- File attachments in messages
- View conversation history
- Delete conversations
- Link messages to specific concerns

### 3.6 Notifications
- View all notifications
- Mark notifications as read
- View notification details
- Notification types: new concerns, overdue concerns, updates

### 3.7 Analytics & Reports
- View analytics dashboard
- Concern statistics (by status, type, priority)
- Resolution time analytics
- Staff performance metrics
- Export analytics reports (PDF)

### 3.8 Profile Management
- View and edit profile information
- Update personal details
- Upload profile image
- Change password

### 3.9 Online Status
- Set online/offline status
- View online staff members
- Last seen tracking

---

## 4. ADMIN FUNCTIONALITIES

### 4.1 Dashboard
- Admin dashboard with system overview
- Comprehensive statistics
- Quick access to key features

### 4.2 User Management
- **User Approval**
  - Approve/reject student registrations
  - Approve/reject SSC staff registrations
  - View pending users
  - Account activation

- **User Management**
  - View all users (Students, SSC, Admin)
  - User search and filter
  - User account management

### 4.3 Concern Management
- **View Concerns**
  - View all concerns system-wide
  - Filter by status, type, priority, student, staff
  - Advanced search functionality

- **Concern Details**
  - View detailed concern information
  - View full concern history
  - View all messages and attachments

- **Respond to Concerns**
  - Respond to concerns with detailed notes
  - Upload response attachments
  - Update responses

- **Resolve Concerns**
  - Resolve concerns with resolution notes
  - Set resolution date

- **Reject Concerns**
  - Reject concerns with rejection reason
  - Track rejection details

- **Export Functionality**
  - Export individual concern as PDF
  - Export all concerns as PDF
  - Generate comprehensive reports

### 4.4 Department & Course Management
- **Department Management**
  - Add new departments
  - Update department information
  - Archive departments
  - Restore archived departments
  - View all departments (active and archived)

- **Course Management**
  - Add new courses to departments
  - Update course information
  - Archive courses
  - Restore archived courses
  - View all courses by department
  - Unique course codes per department

### 4.5 Concern Type Management
- View all concern types
- Add new concern types
- Update existing concern types
- Manage concern type archive status

### 4.6 Analytics & Reports
- **System Analytics**
  - Overall system statistics
  - Concern analytics (by status, type, priority, time period)
  - User statistics
  - Resolution time analysis
  - Export analytics reports (PDF)

### 4.7 Messaging System
- Send messages to students
- Receive messages from students
- File attachments in messages
- View all conversations
- Delete conversations

### 4.8 Notifications
- View all notifications
- System-wide notification management
- Notification types: new concerns, overdue concerns, user approvals, system updates

### 4.9 Activity Logging
- View admin activities
- Track system changes
- Audit trail functionality

### 4.10 Profile Management
- View and edit profile information
- Upload profile image
- Change password

---

## 5. SYSTEM-WIDE FEATURES

### 5.1 Notifications System
- **Notification Types**
  - Concern updates
  - New concern submissions
  - Overdue concern alerts
  - User approval notifications
  - System notifications
  - Reminder notifications (3-day, 5-day)

- **Notification Features**
  - Real-time notifications
  - Read/unread status tracking
  - Notification deletion
  - Bulk operations (mark all read, delete all)
  - Email notifications (via Flask-Mail)

### 5.2 File Management
- **File Upload**
  - Multiple file support per concern
  - File type validation
  - File size validation
  - Secure file storage
  - Original filename preservation

- **File Download**
  - Download concern attachments
  - Download message attachments
  - Secure file access

### 5.3 Email Integration
- Email verification via OTP
- Password reset emails
- Concern response notifications
- System notification emails
- Gmail SMTP integration

### 5.4 Session Management
- Session timeout (30 minutes)
- Activity tracking
- Automatic session expiration
- Secure session cookies

### 5.5 Deadline Management
- Automatic 3-day deadline setting for concerns
- Overdue concern detection
- Deadline notifications
- Tracking of overdue concerns

### 5.6 Online Status Tracking
- Real-time online/offline status
- Last seen timestamp
- Online user indicators
- Status updates via AJAX

### 5.7 Reminder System
- Automatic reminder generation for unresolved concerns
- 3-day reminder notifications
- 5-day reminder notifications
- Reminder checking functionality

### 5.8 Export & Reporting
- **PDF Generation**
  - Individual concern PDF export
  - Bulk concern PDF export
  - Concern history PDF export
  - Analytics report PDF export
  - Timeline PDF export

- **CSV Export**
  - Concerns CSV export
  - Students CSV export
  - Analytics CSV export

### 5.9 Search & Filter
- Advanced search functionality
- Multi-criteria filtering
- Status-based filtering
- Date range filtering
- Type and priority filtering

### 5.10 Security Features
- Password hashing (Werkzeug)
- SQL injection prevention (SQLAlchemy ORM)
- File upload security (secure_filename)
- Session security
- Role-based access control
- CSRF protection considerations

### 5.11 Database Models
- User (legacy)
- Student
- SSC (Student Services Center staff)
- Admin
- Concern
- ConcernAttachment (multiple files per concern)
- ConcernType
- ConcernHistory (audit trail)
- Department
- Course
- Notification
- Message

---

## 6. TECHNICAL FEATURES

### 6.1 Backend
- Flask web framework
- SQLAlchemy ORM
- MySQL database
- File upload handling
- PDF generation (ReportLab)
- CSV generation
- Email integration (Flask-Mail)

### 6.2 Integrations
- OpenAI API integration (prepared)
- Hugging Face API integration (AI chatbot)
- Gmail SMTP for email

### 6.3 Utilities
- Custom template filters (file size formatting)
- Helper functions for deadline management
- Session timeout checking
- Overdue concern checking
- Online status utilities

---

## 7. USER ROLES & PERMISSIONS

### Student Role
- Create and manage own concerns
- View own concerns and history
- Message SSC staff and Admin
- View notifications
- Rate and provide feedback
- Export own concern data

### SSC Staff Role
- View and process all student concerns
- Assign concerns to staff
- Respond to and resolve concerns
- Manage concern types
- View analytics
- Message students
- Export reports

### Admin Role
- Full system access
- User approval/rejection
- Department and course management
- System analytics
- Concern management (all actions)
- System configuration
- Export all reports

---

## 8. CONCERN LIFECYCLE

1. **Submission** - Student submits concern with attachments
2. **Pending** - Concern awaiting review by SSC/Admin
3. **Processing** - SSC/Admin starts processing the concern
4. **Response** - SSC/Admin responds with notes/attachments
5. **Resolved** - Concern marked as resolved with resolution notes
6. **Feedback** - Student provides rating and feedback
7. **Closed** - Concern archived/closed

### Status Flow:
```
Pending → Processing → Resolved → Closed
         ↓
    (Response/Update)
```

---

## 9. NOTIFICATION TRIGGERS

- New concern submitted
- Concern status changed
- Concern assigned to staff
- Concern response added
- Concern resolved
- Concern rejected
- Concern overdue (past deadline)
- Reminder notifications (3-day, 5-day)
- User approval required
- Password reset request

---

## 10. EXPORT CAPABILITIES

### PDF Exports
- Individual concern details
- Bulk concerns report
- Student concern history
- Concern timeline
- Analytics reports

### CSV Exports
- Concerns list
- Students list
- Analytics data

---

This comprehensive functionality list covers all features and capabilities of the PIYUKONEK Student Concern Management System.

