# PIYUKONEK System - Functional Testing Checklist

## Testing Guide
- ☐ = Not tested / Not working
- ✅ = Tested and working
- ❌ = Tested but has issues
- N/A = Not applicable

**Date:** ___________  
**Tester:** ___________

---

## 1. AUTHENTICATION & USER REGISTRATION

### 1.1 Account Type Selection
- [ ] Account type selection page loads correctly
- [ ] All three account types (Student, SSC, Admin) are visible
- [ ] Navigation to each signup page works

### 1.2 Student Registration
- [ ] Student signup page loads correctly
- [ ] All required fields are present (name, username, student ID, email, course, department, year level)
- [ ] File upload fields work (Certificate of Registration, Student ID image)
- [ ] Form validation works (required fields, email format, etc.)
- [ ] Successful registration redirects to OTP verification page
- [ ] OTP email is sent to registered email
- [ ] OTP verification works with correct code
- [ ] OTP verification fails with incorrect code
- [ ] Resend OTP functionality works
- [ ] New student account status is set to "pending"
- [ ] Pending students cannot login before approval
- [ ] Registration prevents duplicate usernames
- [ ] Registration prevents duplicate emails
- [ ] Registration prevents duplicate student ID numbers

### 1.3 SSC Staff Registration
- [ ] SSC signup page loads correctly
- [ ] All required fields are present (name, username, email, position)
- [ ] Form validation works
- [ ] OTP email is sent
- [ ] OTP verification works
- [ ] Resend OTP functionality works
- [ ] New SSC account status is set to "pending"
- [ ] Duplicate username prevention works
- [ ] Duplicate email prevention works

### 1.4 Admin Registration
- [ ] Admin signup page loads correctly
- [ ] All required fields are present
- [ ] Form validation works
- [ ] OTP email is sent
- [ ] OTP verification works
- [ ] Resend OTP functionality works
- [ ] New admin account status is set to "pending"
- [ ] Duplicate username/email prevention works

### 1.5 Login System
- [ ] Login page loads correctly
- [ ] Student login with valid credentials works
- [ ] Student login redirects to student dashboard
- [ ] SSC login with valid credentials works
- [ ] SSC login redirects to SSC dashboard
- [ ] Admin login with valid credentials works
- [ ] Admin login redirects to admin dashboard
- [ ] Login with invalid credentials shows error message
- [ ] Login with pending account shows warning message
- [ ] Password is hashed securely (check database)
- [ ] Session is created upon successful login
- [ ] Session data (user_id, user_type) is stored correctly

### 1.6 Session Management
- [ ] Session expires after 30 minutes of inactivity
- [ ] Session expiration redirects to login page
- [ ] Session activity tracking works
- [ ] Logout functionality works
- [ ] Session is cleared upon logout
- [ ] Cannot access protected pages without login
- [ ] Cannot access pages for other user roles

### 1.7 Password Management
- [ ] Forgot password page loads correctly
- [ ] Password reset email is sent
- [ ] Password reset token is generated correctly
- [ ] Reset password page loads with valid token
- [ ] Reset password page rejects invalid/expired token
- [ ] Password can be reset successfully
- [ ] New password works for login
- [ ] Old password no longer works after reset

---

## 2. ADMIN FUNCTIONALITIES

### 2.1 Admin Dashboard
- [ ] Admin dashboard loads correctly
- [ ] Dashboard displays system statistics
- [ ] Quick access links work
- [ ] Navigation menu works
- [ ] Profile information displays correctly

### 2.2 User Approval
- [ ] User approval page loads correctly
- [ ] Pending students list is displayed
- [ ] Pending SSC staff list is displayed
- [ ] Approve student button works
- [ ] Reject student button works
- [ ] Approved students can login
- [ ] Rejected students cannot login
- [ ] Approval notifications are sent
- [ ] User status changes correctly in database

### 2.3 User Management
- [ ] User management page loads
- [ ] All users (Students, SSC, Admin) are listed
- [ ] Search functionality works
- [ ] Filter functionality works
- [ ] User details are displayed correctly

### 2.4 Department Management
- [ ] Departments page loads correctly
- [ ] View all departments (active and archived)
- [ ] Add new department works
- [ ] Department code must be unique
- [ ] Update department works
- [ ] Archive department works
- [ ] Restore archived department works
- [ ] Department validation works

### 2.5 Course Management
- [ ] Courses page loads correctly
- [ ] View all courses by department
- [ ] Add new course works
- [ ] Course code must be unique within department
- [ ] Update course works
- [ ] Archive course works
- [ ] Restore archived course works
- [ ] Course-department relationship works correctly

### 2.6 Concern Type Management
- [ ] Concern types page loads correctly
- [ ] View all concern types
- [ ] Add new concern type works
- [ ] Update concern type works
- [ ] Archive concern type works
- [ ] Concern type validation works

### 2.7 Concern Management (Admin)
- [ ] View all concerns page loads
- [ ] Filter concerns by status works
- [ ] Filter concerns by type works
- [ ] Filter concerns by priority works
- [ ] Search concerns works
- [ ] View concern details works
- [ ] Respond to concern works
- [ ] Update response works
- [ ] Resolve concern works
- [ ] Reject concern works
- [ ] Rejection reason is required
- [ ] Export individual concern PDF works
- [ ] Export all concerns PDF works

### 2.8 Analytics & Reports (Admin)
- [ ] Analytics page loads correctly
- [ ] Statistics are calculated correctly
- [ ] Charts/graphs display (if implemented)
- [ ] Date range filtering works
- [ ] Export analytics PDF works
- [ ] Data accuracy in reports

### 2.9 Messaging (Admin)
- [ ] Messages page loads correctly
- [ ] View conversations works
- [ ] Send message to student works
- [ ] Receive messages from students
- [ ] File attachments in messages work
- [ ] Delete conversation works
- [ ] Messages linked to concerns display correctly

### 2.10 Notifications (Admin)
- [ ] Notifications page loads
- [ ] View all notifications works
- [ ] Mark notification as read works
- [ ] Notification badges display unread count
- [ ] Delete notification works

### 2.11 Profile Management (Admin)
- [ ] Profile page loads correctly
- [ ] View profile information works
- [ ] Edit profile information works
- [ ] Upload profile image works
- [ ] Profile image displays correctly
- [ ] Change password works

### 2.12 Activity Logging
- [ ] Activity log page loads
- [ ] Admin activities are logged
- [ ] Activities display correctly

---

## 3. SSC STAFF FUNCTIONALITIES

### 3.1 SSC Dashboard
- [ ] SSC dashboard loads correctly
- [ ] Dashboard displays relevant statistics
- [ ] Pending concerns count is accurate
- [ ] Quick actions work
- [ ] Navigation menu works

### 3.2 Concern Management (SSC)
- [ ] View all concerns page loads
- [ ] Filter by status works
- [ ] Filter by type works
- [ ] Filter by priority works
- [ ] Filter by assigned staff works
- [ ] Search concerns works
- [ ] Sort concerns works
- [ ] View concern details works
- [ ] View student information from concern
- [ ] View attachments works

### 3.3 Concern Processing (SSC)
- [ ] Start processing concern works
- [ ] Status changes to "processing"
- [ ] Respond to concern works
- [ ] Upload response attachments works
- [ ] Update response works
- [ ] Resolve concern works
- [ ] Resolution notes are saved
- [ ] Resolution date is set correctly

### 3.4 Concern Assignment
- [ ] View staff list works
- [ ] Assign concern to staff works
- [ ] Assigned staff receives notification
- [ ] View concerns by assigned staff works
- [ ] Bulk assign concerns works

### 3.5 Bulk Operations (SSC)
- [ ] Bulk update status works
- [ ] Bulk assign works
- [ ] Bulk export to CSV works
- [ ] Bulk delete works (if permitted)
- [ ] Bulk operations show confirmation

### 3.6 Student Management (SSC)
- [ ] View all students page loads
- [ ] Search students works
- [ ] View student details works
- [ ] View student concern history works
- [ ] Export students CSV works

### 3.7 Concern Type Management (SSC)
- [ ] View concern types works
- [ ] Add concern type works
- [ ] Update concern type works
- [ ] Validation works

### 3.8 Analytics & Reports (SSC)
- [ ] Analytics page loads
- [ ] Statistics are accurate
- [ ] Export analytics PDF works
- [ ] Charts display correctly (if implemented)

### 3.9 Messaging (SSC)
- [ ] Messages page loads
- [ ] Send message to student works
- [ ] Receive messages from students
- [ ] File attachments work
- [ ] Link messages to concerns works
- [ ] Delete conversation works

### 3.10 Notifications (SSC)
- [ ] Notifications page loads
- [ ] View notifications works
- [ ] Mark as read works
- [ ] Notification badges work
- [ ] View notification details works

### 3.11 Export Functionality (SSC)
- [ ] Export concerns CSV works
- [ ] Export students CSV works
- [ ] Export concern PDF works
- [ ] Export analytics PDF works
- [ ] Files download correctly

### 3.12 Profile Management (SSC)
- [ ] Profile page loads
- [ ] Edit profile works
- [ ] Upload profile image works
- [ ] Change password works

### 3.13 Online Status (SSC)
- [ ] Set online status works
- [ ] Set offline status works
- [ ] Online status displays to others
- [ ] Last seen timestamp updates

---

## 4. STUDENT FUNCTIONALITIES

### 4.1 Student Dashboard
- [ ] Student dashboard loads correctly
- [ ] Dashboard displays personal statistics
- [ ] Quick access to concerns works
- [ ] Quick access to notifications works
- [ ] Profile information displays

### 4.2 Create Concern
- [ ] Create concern page loads
- [ ] All form fields are present
- [ ] Title field works
- [ ] Description field works
- [ ] Concern type dropdown works
- [ ] Priority level selection works
- [ ] Upload multiple files works
- [ ] File type validation works
- [ ] File size validation works
- [ ] Submit concern works
- [ ] Concern is saved with "pending" status
- [ ] Deadline is set (3 days from submission)
- [ ] Notification is sent to SSC/Admin
- [ ] Success message displays

### 4.3 View Concerns
- [ ] View concerns page loads
- [ ] All submitted concerns are listed
- [ ] Filter by status works (pending, processing, resolved, closed)
- [ ] View concern details works
- [ ] View attachments works
- [ ] Download attachments works
- [ ] Concern timeline displays

### 4.4 Edit Concern
- [ ] Edit concern page loads
- [ ] Can edit concern details (if status allows)
- [ ] Update attachments works
- [ ] Remove attachments works
- [ ] Save changes works
- [ ] Cannot edit if already processed

### 4.5 Concern Timeline
- [ ] Timeline page loads
- [ ] Timeline displays all status changes
- [ ] Timeline is in chronological order
- [ ] Download timeline PDF works
- [ ] Timeline includes all actions

### 4.6 Rate & Feedback
- [ ] Rate concern option appears for resolved concerns
- [ ] Rating system works (1-5 stars)
- [ ] Submit feedback works
- [ ] Feedback is saved
- [ ] Cannot rate multiple times
- [ ] Feedback displays correctly

### 4.7 Attachment Management
- [ ] Upload multiple attachments works
- [ ] View attachment list works
- [ ] Download attachment works
- [ ] Remove attachment works
- [ ] Attachment details display correctly

### 4.8 Export Functionality (Student)
- [ ] Export concern history PDF works
- [ ] Export concern details PDF works
- [ ] PDF contains correct information
- [ ] Statistics in PDF are accurate
- [ ] Files download correctly

### 4.9 Messaging (Student)
- [ ] Messages page loads
- [ ] Send message to SSC/Admin works
- [ ] Receive messages works
- [ ] File attachments in messages work
- [ ] Link messages to concerns works
- [ ] View conversation history works
- [ ] Delete conversation works

### 4.10 Notifications (Student)
- [ ] Notifications page loads
- [ ] View all notifications works
- [ ] Mark notification as read works
- [ ] Mark all as read works
- [ ] Delete notification works
- [ ] Delete all notifications works
- [ ] Notification badges display unread count
- [ ] Notifications update in real-time (if implemented)

### 4.11 Profile Management (Student)
- [ ] Profile page loads
- [ ] View profile information works
- [ ] Edit profile information works
- [ ] Upload profile image works
- [ ] Profile image displays correctly
- [ ] Change password works

### 4.12 Reminders
- [ ] Reminders page loads
- [ ] Reminders for unresolved concerns display
- [ ] 3-day reminders work
- [ ] 5-day reminders work

### 4.13 AI Chatbot
- [ ] Chatbot interface loads
- [ ] Submit concern to chatbot works
- [ ] AI response is generated
- [ ] Response is relevant
- [ ] Error handling works if API fails

---

## 5. SYSTEM-WIDE FEATURES

### 5.1 Notifications System
- [ ] Notification creation works
- [ ] Notification types are correct
- [ ] Notifications are sent to correct users
- [ ] Email notifications are sent (if configured)
- [ ] Notification badges update
- [ ] Read/unread status tracking works
- [ ] Notification deletion works

### 5.2 File Management
- [ ] File upload works
- [ ] Multiple files can be uploaded
- [ ] File types are validated
- [ ] File sizes are validated
- [ ] Files are stored securely
- [ ] File download works
- [ ] File access is restricted appropriately
- [ ] Original filenames are preserved
- [ ] File size display works

### 5.3 Email Integration
- [ ] OTP emails are sent
- [ ] Password reset emails are sent
- [ ] Concern notification emails are sent
- [ ] Response notification emails are sent
- [ ] Email templates render correctly
- [ ] Email delivery is reliable

### 5.4 Deadline Management
- [ ] Deadline is set automatically (3 days)
- [ ] Overdue concerns are detected
- [ ] Overdue notifications are created
- [ ] Deadline tracking is accurate

### 5.5 Online Status
- [ ] Online status updates correctly
- [ ] Last seen timestamp updates
- [ ] Online users display correctly
- [ ] Offline status is set on logout

### 5.6 Reminder System
- [ ] Reminders are generated automatically
- [ ] 3-day reminders work
- [ ] 5-day reminders work
- [ ] Reminder notifications are sent
- [ ] Reminder checking works

### 5.7 Export & Reporting
- [ ] PDF generation works
- [ ] CSV export works
- [ ] Export files are formatted correctly
- [ ] Data in exports is accurate
- [ ] File downloads work
- [ ] Export filenames are correct

### 5.8 Search & Filter
- [ ] Search functionality works
- [ ] Filter by status works
- [ ] Filter by type works
- [ ] Filter by priority works
- [ ] Filter by date range works
- [ ] Multiple filters work together
- [ ] Search results are accurate

### 5.9 Security Features
- [ ] Passwords are hashed
- [ ] SQL injection prevention works
- [ ] File upload security works
- [ ] Session security works
- [ ] Role-based access control works
- [ ] Unauthorized access is blocked

### 5.10 Database Integrity
- [ ] All relationships work correctly
- [ ] Foreign keys are enforced
- [ ] Data consistency is maintained
- [ ] Unique constraints work
- [ ] Cascade deletes work (if applicable)

### 5.11 UI/UX
- [ ] All pages load without errors
- [ ] Navigation is intuitive
- [ ] Forms are user-friendly
- [ ] Error messages are clear
- [ ] Success messages display
- [ ] Responsive design works (if implemented)
- [ ] Images load correctly
- [ ] CSS styling is applied

### 5.12 Error Handling
- [ ] Invalid inputs show error messages
- [ ] 404 errors are handled
- [ ] 500 errors are handled gracefully
- [ ] Database errors are caught
- [ ] File upload errors are handled
- [ ] API errors are handled (chatbot)

---

## 6. INTEGRATION TESTING

### 6.1 User Workflows
- [ ] Complete student registration → approval → login → submit concern → receive response workflow
- [ ] Complete SSC staff registration → approval → login → process concern → resolve workflow
- [ ] Complete concern submission → processing → resolution → feedback workflow
- [ ] Complete password reset workflow
- [ ] Complete messaging workflow between student and SSC/Admin

### 6.2 Multi-User Scenarios
- [ ] Multiple students can submit concerns simultaneously
- [ ] Multiple SSC staff can process different concerns
- [ ] Admin can approve multiple users
- [ ] Bulk operations work with multiple records

### 6.3 Data Consistency
- [ ] Concern status changes reflect across all views
- [ ] Notification counts are accurate
- [ ] Statistics update correctly
- [ ] User actions are logged correctly

---

## 7. PERFORMANCE TESTING

### 7.1 Page Load Times
- [ ] Dashboard loads within acceptable time
- [ ] Concern list page loads quickly
- [ ] Large file uploads work
- [ ] Export generation is acceptable

### 7.2 Database Performance
- [ ] Queries are optimized
- [ ] Large datasets load without timeout
- [ ] Search queries are fast

### 7.3 File Handling
- [ ] Large files can be uploaded
- [ ] Multiple files upload successfully
- [ ] File downloads are fast

---

## 8. BROWSER COMPATIBILITY

- [ ] Works on Chrome
- [ ] Works on Firefox
- [ ] Works on Edge
- [ ] Works on Safari (if applicable)
- [ ] Mobile responsiveness (if implemented)

---

## 9. SECURITY TESTING

- [ ] SQL injection attempts are blocked
- [ ] XSS (Cross-Site Scripting) attempts are blocked
- [ ] CSRF protection works
- [ ] File upload restrictions work
- [ ] Unauthorized file access is prevented
- [ ] Session hijacking is prevented
- [ ] Password requirements are enforced

---

## 10. DOCUMENTATION VERIFICATION

- [ ] User documentation is accurate
- [ ] System documentation is complete
- [ ] API documentation exists (if applicable)
- [ ] Installation guide is accurate

---

## Notes Section

**Critical Issues Found:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Minor Issues Found:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Suggestions for Improvement:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Overall System Status:** ☐ Ready for Production  ☐ Needs Fixes  ☐ Not Ready

**Test Completion Date:** ___________

**Approved By:** ___________  
**Signature:** ___________

