# PIYUKONEK - Student Concern Management System
# Test Case Scenarios Document

---

## Project Information
- **System Name:** Piyukonek (Student Concern Management System)
- **Version:** 1.0
- **Test Date:** _______________
- **Tested By:** _______________

---

## Legend
| Status | Description |
|--------|-------------|
| **PASS** | Test executed successfully, actual result matches expected result |
| **FAIL** | Test executed but actual result does not match expected result |
| **N/T** | Not Tested |

---

# MODULE 1: USER AUTHENTICATION

## Test Case 1.1: Student Login with Valid Credentials

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to the login page (http://localhost:5000/login) | Login page is displayed with username and password fields | | |
| 2 | Enter a valid student username in the username field | Username is accepted and displayed in the field | | |
| 3 | Enter the correct password for the student account | Password is masked and accepted | | |
| 4 | Click the "Login" button | System validates credentials and redirects to Student Dashboard | | |
| 5 | Verify the dashboard displays student information | Student name, concerns, and navigation menu are displayed | | |

---

## Test Case 1.2: Student Login with Invalid Credentials

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to the login page | Login page is displayed | | |
| 2 | Enter an invalid username (e.g., "invaliduser123") | Username is accepted in the field | | |
| 3 | Enter any password | Password is accepted in the field | | |
| 4 | Click the "Login" button | Error message "Invalid username or password" is displayed | | |
| 5 | Verify user remains on the login page | User is not redirected, login form is still visible | | |

---

## Test Case 1.3: SSC (Guidance) Staff Login

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to the login page | Login page is displayed | | |
| 2 | Enter valid SSC staff username | Username is accepted | | |
| 3 | Enter correct password for SSC account | Password is accepted | | |
| 4 | Click the "Login" button | System redirects to SSC Dashboard | | |
| 5 | Verify SSC dashboard with concern management features | Concerns list, students list, notifications are visible | | |

---

## Test Case 1.4: Admin Login

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to the login page | Login page is displayed | | |
| 2 | Enter valid admin username | Username is accepted | | |
| 3 | Enter correct password for admin account | Password is accepted | | |
| 4 | Click the "Login" button | System redirects to Admin Dashboard | | |
| 5 | Verify admin dashboard with full management features | User management, analytics, departments are visible | | |

---

## Test Case 1.5: Login with Pending Account Status

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to the login page | Login page is displayed | | |
| 2 | Enter username of a pending (not yet approved) account | Username is accepted | | |
| 3 | Enter the correct password | Password is accepted | | |
| 4 | Click the "Login" button | Warning message "Your account is pending approval by admin" displayed | | |
| 5 | Verify user is not logged in | User remains on login page, no session created | | |

---

## Test Case 1.6: User Logout

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login with any valid user account | User is logged in and redirected to dashboard | | |
| 2 | Click the "Logout" button/link | System processes logout request | | |
| 3 | Verify session is cleared | User is redirected to login page | | |
| 4 | Try to access dashboard directly via URL | System redirects to login page with "Please log in" message | | |

---

## Test Case 1.7: Session Timeout (30 minutes)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login with valid credentials | User is logged in successfully | | |
| 2 | Leave the system idle for more than 30 minutes | Session timeout timer starts | | |
| 3 | Try to perform any action after 30 minutes | System displays "Your session has expired. Please log in again." | | |
| 4 | Verify user is redirected to login page | Login page is displayed | | |

---

# MODULE 2: USER REGISTRATION

## Test Case 2.1: Student Registration with Valid Data

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to Account Type page (/account_type) | Page displays registration options (Student, SSC, Admin) | | |
| 2 | Click on "Student" registration option | Student signup form is displayed | | |
| 3 | Fill in Full Name (e.g., "Juan Dela Cruz") | Field accepts the input | | |
| 4 | Fill in unique Username (e.g., "juandc2024") | Field accepts the input | | |
| 5 | Fill in Student ID Number (e.g., "2024-12345") | Field accepts the input | | |
| 6 | Fill in valid Email Address (e.g., "juan@example.com") | Field accepts the input | | |
| 7 | Select Course from dropdown | Course is selected | | |
| 8 | Select College/Department from dropdown | Department is selected | | |
| 9 | Select Year Level from dropdown | Year level is selected | | |
| 10 | Upload Certificate of Registration (PDF/Image) | File is accepted and shown | | |
| 11 | Upload Student ID (Image) | File is accepted and shown | | |
| 12 | Enter Password meeting requirements | Password is accepted | | |
| 13 | Confirm Password (same as Step 12) | Password confirmation matches | | |
| 14 | Click "Register" button | OTP is sent to email, OTP verification page displayed | | |

---

## Test Case 2.2: Student Registration - OTP Verification

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Complete student registration form (Test Case 2.1) | OTP verification page is displayed | | |
| 2 | Check email for OTP code | 6-digit OTP code received in email | | |
| 3 | Enter the correct OTP code | OTP is accepted in the field | | |
| 4 | Click "Verify" button | Account created successfully, pending admin approval | | |
| 5 | Verify success message displayed | "Registration successful! Please wait for admin approval" | | |

---

## Test Case 2.3: Student Registration - Invalid OTP

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Complete student registration form | OTP verification page is displayed | | |
| 2 | Enter an incorrect OTP code (e.g., "000000") | OTP is entered in the field | | |
| 3 | Click "Verify" button | Error message "Invalid OTP" is displayed | | |
| 4 | Verify user can retry | OTP field is cleared, user can enter again | | |

---

## Test Case 2.4: Student Registration - Resend OTP

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Complete student registration form | OTP verification page is displayed | | |
| 2 | Click "Resend OTP" button | New OTP is generated and sent to email | | |
| 3 | Verify new OTP email received | New 6-digit OTP code received | | |
| 4 | Enter the new OTP code and verify | Account created successfully | | |

---

## Test Case 2.5: Student Registration - Duplicate Username

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to student signup form | Form is displayed | | |
| 2 | Enter a username that already exists in the system | Username is entered | | |
| 3 | Fill in all other required fields | Fields are filled | | |
| 4 | Click "Register" button | Error message "Username already exists" displayed | | |
| 5 | Verify registration is not processed | User remains on form, no OTP sent | | |

---

## Test Case 2.6: Student Registration - Duplicate Email

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to student signup form | Form is displayed | | |
| 2 | Enter an email that already exists in the system | Email is entered | | |
| 3 | Fill in all other required fields with unique values | Fields are filled | | |
| 4 | Click "Register" button | Error message "Email already exists" displayed | | |
| 5 | Verify registration is not processed | User remains on form | | |

---

## Test Case 2.7: SSC Staff Registration

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to Account Type page | Registration options displayed | | |
| 2 | Click on "SSC" registration option | SSC signup form is displayed | | |
| 3 | Fill in Full Name | Field accepts input | | |
| 4 | Fill in unique Username | Field accepts input | | |
| 5 | Fill in valid Email Address | Field accepts input | | |
| 6 | Select Position (e.g., Guidance Coordinator) | Position is selected | | |
| 7 | Enter Password | Password is accepted | | |
| 8 | Confirm Password | Password matches | | |
| 9 | Click "Register" button | OTP sent to email, verification page displayed | | |
| 10 | Enter OTP and verify | Account created, pending admin approval | | |

---

## Test Case 2.8: Admin Registration

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to Account Type page | Registration options displayed | | |
| 2 | Click on "Admin" registration option | Admin signup form is displayed | | |
| 3 | Fill in Full Name | Field accepts input | | |
| 4 | Fill in unique Username | Field accepts input | | |
| 5 | Fill in valid Email Address | Field accepts input | | |
| 6 | Enter Password | Password is accepted | | |
| 7 | Confirm Password | Password matches | | |
| 8 | Click "Register" button | OTP sent to email, verification page displayed | | |
| 9 | Enter OTP and verify | Account created successfully | | |

---

# MODULE 3: PASSWORD RECOVERY

## Test Case 3.1: Forgot Password - Valid Email

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to login page | Login page displayed | | |
| 2 | Click "Forgot Password" link | Forgot password page displayed | | |
| 3 | Enter registered email address | Email is accepted | | |
| 4 | Click "Send Reset Link" button | Password reset email sent | | |
| 5 | Check email for reset link | Email received with reset link | | |
| 6 | Click the reset link | Password reset form displayed | | |
| 7 | Enter new password | Password accepted | | |
| 8 | Confirm new password | Password matches | | |
| 9 | Click "Reset Password" button | Password updated successfully | | |
| 10 | Login with new password | Login successful | | |

---

## Test Case 3.2: Forgot Password - Invalid Email

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Navigate to Forgot Password page | Page displayed | | |
| 2 | Enter an unregistered email address | Email entered | | |
| 3 | Click "Send Reset Link" button | Error message "Email not found" or generic message | | |
| 4 | Verify no email sent | No reset email received | | |

---

## Test Case 3.3: Forgot Password - Expired Reset Link

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Request password reset | Reset link sent to email | | |
| 2 | Wait until link expires (token timeout) | Link becomes invalid | | |
| 3 | Click the expired reset link | Error message "Reset link expired" displayed | | |
| 4 | Verify user is prompted to request new link | Option to request new link shown | | |

---

# MODULE 4: STUDENT CONCERN SUBMISSION

## Test Case 4.1: Submit Concern with All Required Fields

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as an active student | Student dashboard displayed | | |
| 2 | Navigate to "Submit Concern" page | Concern submission form displayed | | |
| 3 | Select Concern Type from dropdown (e.g., Academic) | Type is selected | | |
| 4 | Enter Concern Title (e.g., "Grade Inquiry") | Title is accepted | | |
| 5 | Enter Concern Description with details | Description is accepted | | |
| 6 | Click "Submit" button | Concern submitted successfully | | |
| 7 | Verify success message | "Your concern is submitted and must be reviewed" displayed | | |
| 8 | Verify concern appears in student's concern list | New concern visible with "Pending" status | | |

---

## Test Case 4.2: Submit Concern with File Attachments

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student and navigate to Submit Concern | Form displayed | | |
| 2 | Fill in Concern Type, Title, and Description | Fields populated | | |
| 3 | Click "Upload Files" and select 1 PDF file | File uploaded, filename displayed | | |
| 4 | Add another file (JPG image) | Second file uploaded | | |
| 5 | Add third file (DOC document) | Third file uploaded | | |
| 6 | Click "Submit" button | Concern submitted with 3 attachments | | |
| 7 | Verify attachments are saved | Attachments visible in concern details | | |

---

## Test Case 4.3: Submit Concern - Exceed Maximum File Limit

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student, navigate to Submit Concern | Form displayed | | |
| 2 | Fill in required fields | Fields populated | | |
| 3 | Attempt to upload more than 3 files | System should prevent or show error | | |
| 4 | Verify error message | "You can upload a maximum of 3 files" displayed | | |

---

## Test Case 4.4: Submit Concern - Invalid File Type

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student, navigate to Submit Concern | Form displayed | | |
| 2 | Fill in required fields | Fields populated | | |
| 3 | Attempt to upload a file with invalid extension (e.g., .exe) | File selection attempted | | |
| 4 | Click Submit | Error "Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT" | | |
| 5 | Verify concern is not submitted | User remains on form | | |

---

## Test Case 4.5: Submit Concern - File Size Exceeds Limit (10MB)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student, navigate to Submit Concern | Form displayed | | |
| 2 | Fill in required fields | Fields populated | | |
| 3 | Attempt to upload a file larger than 10MB | File selection attempted | | |
| 4 | Click Submit | Error "File is too large. Maximum size is 10MB" displayed | | |
| 5 | Verify concern is not submitted | User remains on form | | |

---

## Test Case 4.6: Submit Concern - Exceed Pending Concern Limit

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student who already has 2 pending concerns | Dashboard displayed | | |
| 2 | Navigate to Submit Concern page | Form displayed | | |
| 3 | Fill in all required fields | Fields populated | | |
| 4 | Click "Submit" button | Error message displayed | | |
| 5 | Verify error | "You have reached the maximum limit of 2 pending concerns" | | |
| 6 | Verify concern is not created | No new concern added | | |

---

## Test Case 4.7: Submit Concern - Missing Required Fields

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student, navigate to Submit Concern | Form displayed | | |
| 2 | Leave Concern Type empty | Field is empty | | |
| 3 | Fill in Title and Description | Fields populated | | |
| 4 | Click "Submit" button | Error "All fields are required" displayed | | |
| 5 | Verify concern is not submitted | User remains on form | | |

---

## Test Case 4.8: Edit Pending Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student with a pending concern | Dashboard displayed | | |
| 2 | Navigate to concern details | Concern details page displayed | | |
| 3 | Click "Edit" button | Edit concern form displayed with current data | | |
| 4 | Modify the concern title | New title entered | | |
| 5 | Modify the concern description | New description entered | | |
| 6 | Click "Save Changes" button | Concern updated successfully | | |
| 7 | Verify changes saved | Updated title and description displayed | | |

---

# MODULE 5: CONCERN MANAGEMENT (SSC/GUIDANCE)

## Test Case 5.1: View All Concerns (SSC Dashboard)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to "Concerns" section | List of all concerns displayed | | |
| 3 | Verify concern information displayed | ID, Title, Student, Type, Priority, Status visible | | |
| 4 | Verify filtering options available | Filter by status, type, priority available | | |
| 5 | Verify search functionality | Search bar for concerns available | | |

---

## Test Case 5.2: Update Concern Priority

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to a specific concern | Concern details displayed | | |
| 3 | Change priority level from "Medium" to "High" | Priority dropdown shows options | | |
| 4 | Click "Update Priority" button | Priority updated successfully | | |
| 5 | Verify new priority displayed | "High" priority now shown | | |
| 6 | Verify notification sent to student | Student notified of priority change | | |

---

## Test Case 5.3: Respond to Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to a pending concern | Concern details displayed | | |
| 3 | Enter response notes in the response field | Notes entered | | |
| 4 | Optionally upload response attachment | File uploaded | | |
| 5 | Click "Submit Response" button | Response saved, status changed to "Processing" | | |
| 6 | Verify status update | Concern status shows "Processing" | | |
| 7 | Verify student notification | Student notified of response | | |

---

## Test Case 5.4: Resolve Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to a "Processing" concern | Concern details displayed | | |
| 3 | Enter resolution notes | Notes entered | | |
| 4 | Click "Mark as Resolved" button | Concern marked as resolved | | |
| 5 | Verify status changed to "Resolved" | "Resolved" status displayed | | |
| 6 | Verify resolved_at timestamp recorded | Timestamp visible | | |
| 7 | Verify student notification | Student notified concern is resolved | | |

---

## Test Case 5.5: Bulk Update Concern Status

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to concerns list | Concerns displayed | | |
| 3 | Select multiple concerns using checkboxes | 3 concerns selected | | |
| 4 | Select "Processing" from bulk action dropdown | Status option selected | | |
| 5 | Click "Apply" button | All selected concerns updated | | |
| 6 | Verify all selected concerns have new status | "Processing" status for all 3 | | |

---

## Test Case 5.6: Bulk Assign Concerns to Staff

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff (Coordinator/Supervisor) | Dashboard displayed | | |
| 2 | Navigate to concerns list | Concerns displayed | | |
| 3 | Select multiple pending concerns | Concerns selected | | |
| 4 | Click "Bulk Assign" | Staff selection modal appears | | |
| 5 | Select SSC staff member from dropdown | Staff selected | | |
| 6 | Click "Assign" button | Concerns assigned successfully | | |
| 7 | Verify assigned_to field updated | Selected staff assigned to concerns | | |

---

## Test Case 5.7: Bulk Export Concerns

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | Dashboard displayed | | |
| 2 | Navigate to concerns list | Concerns displayed | | |
| 3 | Select concerns to export | Concerns selected | | |
| 4 | Click "Export" button | Export options displayed | | |
| 5 | Select export format (CSV/PDF) | Format selected | | |
| 6 | Click "Download" | File downloaded | | |
| 7 | Verify file contains selected concerns | Data accurate in exported file | | |

---

## Test Case 5.8: View Student List (SSC)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to "Students" section | List of students displayed | | |
| 3 | Verify student information shown | Name, ID, Course, Department, Status visible | | |
| 4 | Click on a student name | Student details page displayed | | |
| 5 | View student's concern history | All concerns by this student listed | | |

---

# MODULE 6: CONCERN MANAGEMENT (ADMIN)

## Test Case 6.1: Admin View All Concerns

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "Concerns" section | All concerns listed | | |
| 3 | Verify full concern data visible | All concern details accessible | | |
| 4 | Verify admin-specific actions available | Respond, Resolve, Reject options visible | | |

---

## Test Case 6.2: Admin Respond to Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to a pending concern | Concern details displayed | | |
| 3 | Enter response notes | Notes entered | | |
| 4 | Upload response attachment (optional) | File attached | | |
| 5 | Click "Submit Response" button | Response saved | | |
| 6 | Verify responded_by and responded_at recorded | Admin ID and timestamp saved | | |
| 7 | Verify notifications sent | Student and SSC notified | | |

---

## Test Case 6.3: Admin Reject Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to a concern | Concern details displayed | | |
| 3 | Click "Reject" button | Rejection form displayed | | |
| 4 | Enter rejection reason | Reason entered | | |
| 5 | Confirm rejection | Concern rejected | | |
| 6 | Verify status changed to "Rejected" | Status updated | | |
| 7 | Verify rejection_reason, rejected_by, rejected_at saved | Data recorded | | |
| 8 | Verify student notification | Student notified of rejection | | |

---

## Test Case 6.4: Admin Update Response

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to a concern with existing response | Concern with response displayed | | |
| 3 | Modify the response notes | Notes updated | | |
| 4 | Click "Update Response" button | Response updated | | |
| 5 | Verify updated response saved | New response visible | | |

---

## Test Case 6.5: Export Concern to PDF (Admin)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to a specific concern | Concern details displayed | | |
| 3 | Click "Export to PDF" button | PDF generation initiated | | |
| 4 | Verify PDF downloads | PDF file downloaded | | |
| 5 | Open PDF and verify content | All concern details included | | |

---

# MODULE 7: USER MANAGEMENT (ADMIN)

## Test Case 7.1: View User Approval Requests

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "User Approval" section | Pending users listed | | |
| 3 | Verify pending students visible | Students with "pending" status shown | | |
| 4 | Verify pending SSC staff visible | SSC with "pending" status shown | | |

---

## Test Case 7.2: Approve Student Account

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to User Approval | Pending users listed | | |
| 3 | Locate a pending student account | Student visible | | |
| 4 | Click "Approve" button | Confirmation prompt displayed | | |
| 5 | Confirm approval | Account approved | | |
| 6 | Verify student status changed to "active" | Status updated | | |
| 7 | Verify student can now login | Student login successful | | |

---

## Test Case 7.3: Reject Student Account

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to User Approval | Pending users listed | | |
| 3 | Locate a pending student account | Student visible | | |
| 4 | Click "Reject" button | Confirmation prompt displayed | | |
| 5 | Confirm rejection | Account rejected | | |
| 6 | Verify student removed or marked inactive | Status updated | | |

---

## Test Case 7.4: Approve SSC Account

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to User Approval | Pending users listed | | |
| 3 | Locate a pending SSC account | SSC visible | | |
| 4 | Click "Approve" button | Confirmation displayed | | |
| 5 | Confirm approval | Account approved | | |
| 6 | Verify SSC status changed to "active" | Status updated | | |

---

## Test Case 7.5: Reject SSC Account

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to User Approval | Pending users listed | | |
| 3 | Locate a pending SSC account | SSC visible | | |
| 4 | Click "Reject" button | Confirmation displayed | | |
| 5 | Confirm rejection | Account rejected | | |
| 6 | Verify SSC status updated | Account inactive or removed | | |

---

## Test Case 7.6: View All Users

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "User Management" | User list displayed | | |
| 3 | Verify students listed | All students with details shown | | |
| 4 | Verify SSC staff listed | All SSC with details shown | | |
| 5 | Verify filtering/search available | Can filter by type, status | | |

---

# MODULE 8: DEPARTMENT AND COURSE MANAGEMENT

## Test Case 8.1: Add New Department

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "Departments" section | Departments page displayed | | |
| 3 | Click "Add Department" button | Add form displayed | | |
| 4 | Enter Department Name (e.g., "College of Engineering") | Name entered | | |
| 5 | Enter Department Code (e.g., "COE") | Code entered | | |
| 6 | Enter Description (optional) | Description entered | | |
| 7 | Click "Save" button | Department created | | |
| 8 | Verify department appears in list | New department visible | | |

---

## Test Case 8.2: Add Duplicate Department Code

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Departments, click "Add Department" | Form displayed | | |
| 3 | Enter a department code that already exists | Code entered | | |
| 4 | Fill other fields and click "Save" | Error displayed | | |
| 5 | Verify error message | "Department code already exists" | | |

---

## Test Case 8.3: Update Department

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Departments | Departments listed | | |
| 3 | Click "Edit" on an existing department | Edit form displayed | | |
| 4 | Modify department name | Name changed | | |
| 5 | Click "Update" button | Department updated | | |
| 6 | Verify changes saved | Updated name displayed | | |

---

## Test Case 8.4: Archive Department

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Departments | Departments listed | | |
| 3 | Click "Archive" on a department | Confirmation displayed | | |
| 4 | Confirm archive action | Department archived | | |
| 5 | Verify status changed to "archived" | Department moved to archived | | |
| 6 | Verify department not available in dropdowns | Not shown in student registration | | |

---

## Test Case 8.5: Restore Archived Department

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Departments, view archived | Archived departments shown | | |
| 3 | Click "Restore" on an archived department | Confirmation displayed | | |
| 4 | Confirm restore action | Department restored | | |
| 5 | Verify status changed to "active" | Department back in active list | | |

---

## Test Case 8.6: Add New Course

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "Courses" section | Courses page displayed | | |
| 3 | Click "Add Course" button | Add form displayed | | |
| 4 | Select Department from dropdown | Department selected | | |
| 5 | Enter Course Name (e.g., "BS Computer Science") | Name entered | | |
| 6 | Enter Course Code (e.g., "BSCS") | Code entered | | |
| 7 | Enter Description (optional) | Description entered | | |
| 8 | Click "Save" button | Course created | | |
| 9 | Verify course appears in list | New course visible | | |

---

## Test Case 8.7: Update Course

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Courses | Courses listed | | |
| 3 | Click "Edit" on an existing course | Edit form displayed | | |
| 4 | Modify course name | Name changed | | |
| 5 | Click "Update" button | Course updated | | |
| 6 | Verify changes saved | Updated name displayed | | |

---

## Test Case 8.8: Archive and Restore Course

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Courses | Courses listed | | |
| 3 | Archive a course | Course archived | | |
| 4 | Verify course status "archived" | Status updated | | |
| 5 | Restore the archived course | Course restored | | |
| 6 | Verify course status "active" | Status updated | | |

---

# MODULE 9: CONCERN TYPES MANAGEMENT

## Test Case 9.1: Add New Concern Type (SSC)

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to "Concern Types" management | Concern types page displayed | | |
| 3 | Click "Add Type" button | Add form displayed | | |
| 4 | Enter new concern type name (e.g., "Scholarship") | Name entered | | |
| 5 | Click "Save" button | Concern type created | | |
| 6 | Verify type appears in list | New type visible | | |
| 7 | Verify type available in student concern form | Type selectable | | |

---

## Test Case 9.2: Add Duplicate Concern Type

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Concern Types, click "Add Type" | Form displayed | | |
| 3 | Enter a concern type name that already exists | Name entered | | |
| 4 | Click "Save" button | Error displayed | | |
| 5 | Verify error message | "Concern type already exists" | | |

---

## Test Case 9.3: Archive Concern Type

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Concern Types | Types listed | | |
| 3 | Click "Archive" on a concern type | Confirmation displayed | | |
| 4 | Confirm archive | Type archived | | |
| 5 | Verify type is_archived = true | Status updated | | |
| 6 | Verify type not available in student form | Type not selectable | | |

---

# MODULE 10: NOTIFICATIONS

## Test Case 10.1: View Student Notifications

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to "Notifications" | Notifications page displayed | | |
| 3 | Verify notifications listed | List of notifications shown | | |
| 4 | Verify unread count displayed | Badge shows unread count | | |
| 5 | Verify notification types filterable | Filter by concern_update, system, general | | |

---

## Test Case 10.2: Mark Notification as Read

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student with unread notifications | Notifications visible | | |
| 2 | Click on an unread notification | Notification opened | | |
| 3 | Verify notification marked as read | is_read = true | | |
| 4 | Verify unread count decremented | Badge count reduced | | |

---

## Test Case 10.3: Mark All Notifications as Read

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student with multiple unread notifications | Notifications visible | | |
| 2 | Click "Mark All as Read" button | All notifications processed | | |
| 3 | Verify all notifications is_read = true | Status updated for all | | |
| 4 | Verify unread count is 0 | Badge shows 0 or hidden | | |

---

## Test Case 10.4: Delete Notification

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Notifications page | | |
| 2 | Click "Delete" on a notification | Confirmation displayed | | |
| 3 | Confirm deletion | Notification deleted | | |
| 4 | Verify notification removed from list | Not visible in list | | |

---

## Test Case 10.5: Delete All Notifications

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Notifications page | | |
| 2 | Click "Delete All" button | Confirmation displayed | | |
| 3 | Confirm deletion | All notifications deleted | | |
| 4 | Verify notification list empty | "No notifications" message | | |

---

## Test Case 10.6: SSC Receives New Concern Notification

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Student submits a new concern | Concern created | | |
| 2 | Login as SSC staff (Coordinator/Supervisor) | SSC dashboard displayed | | |
| 3 | Check notifications | New notification received | | |
| 4 | Verify notification title | "New Concern Submitted" | | |
| 5 | Verify notification links to concern | Click opens concern details | | |

---

# MODULE 11: MESSAGING/CHAT

## Test Case 11.1: Student Send Message

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to Messages/Chat section | Chat interface displayed | | |
| 3 | Select recipient (SSC/Admin) | Recipient selected | | |
| 4 | Type message content | Message entered | | |
| 5 | Click "Send" button | Message sent | | |
| 6 | Verify message appears in chat | Message visible with timestamp | | |

---

## Test Case 11.2: Send Message with Attachment

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to Messages | Chat interface displayed | | |
| 3 | Type message content | Message entered | | |
| 4 | Click attachment button and select file | File attached | | |
| 5 | Click "Send" | Message with attachment sent | | |
| 6 | Verify attachment downloadable | Click downloads file | | |

---

## Test Case 11.3: SSC Reply to Message

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Messages | Message list displayed | | |
| 3 | Select conversation with student | Chat history shown | | |
| 4 | Type reply message | Message entered | | |
| 5 | Click "Send" | Reply sent | | |
| 6 | Verify message in conversation | Reply visible | | |

---

## Test Case 11.4: Delete Conversation

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Messages | Conversations listed | | |
| 3 | Click "Delete" on a conversation | Confirmation displayed | | |
| 4 | Confirm deletion | Conversation deleted | | |
| 5 | Verify conversation removed | Not in list | | |

---

# MODULE 12: PROFILE MANAGEMENT

## Test Case 12.1: Update Student Profile

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to Profile settings | Profile page displayed | | |
| 3 | Verify current profile information | Data displayed | | |
| 4 | Upload new profile image | Image uploaded | | |
| 5 | Click "Save Changes" | Profile updated | | |
| 6 | Verify new image displayed | Image shows in profile | | |

---

## Test Case 12.2: Update SSC Profile

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Profile settings | Profile page displayed | | |
| 3 | Update profile image | Image uploaded | | |
| 4 | Click "Save Changes" | Profile updated | | |
| 5 | Verify changes saved | Updated image displayed | | |

---

## Test Case 12.3: Update Admin Profile Image

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Profile settings | Profile page displayed | | |
| 3 | Click "Upload Profile Image" | File dialog opens | | |
| 4 | Select new image | Image uploaded | | |
| 5 | Verify new image displayed | Image updated in profile | | |

---

# MODULE 13: ANALYTICS AND REPORTS

## Test Case 13.1: View Admin Analytics Dashboard

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to "Analytics" | Analytics page displayed | | |
| 3 | Verify total concerns count | Count displayed | | |
| 4 | Verify concerns by status chart | Pie/bar chart visible | | |
| 5 | Verify concerns by type breakdown | Type distribution shown | | |
| 6 | Verify concerns by priority | Priority distribution shown | | |
| 7 | Verify time-based trends | Graph showing trends | | |

---

## Test Case 13.2: Export Admin Analytics

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as admin | Admin dashboard displayed | | |
| 2 | Navigate to Analytics | Analytics displayed | | |
| 3 | Click "Export" button | Export options displayed | | |
| 4 | Select format (CSV/PDF) | Format selected | | |
| 5 | Click "Download" | File downloaded | | |
| 6 | Verify exported data | Analytics data in file | | |

---

## Test Case 13.3: View SSC Analytics

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to "Analytics" | SSC analytics displayed | | |
| 3 | Verify concern statistics | Stats visible | | |
| 4 | Verify student-related metrics | Student data shown | | |
| 5 | Verify performance metrics | Resolution times, etc. | | |

---

## Test Case 13.4: Export SSC Analytics

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Navigate to Analytics | Analytics displayed | | |
| 3 | Click "Export" | Export initiated | | |
| 4 | Verify file downloads | File downloaded | | |

---

# MODULE 14: STUDENT CONCERN FEEDBACK

## Test Case 14.1: Submit Concern Rating/Feedback

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to a resolved concern | Concern details displayed | | |
| 3 | Verify feedback form available | Rating and feedback fields shown | | |
| 4 | Select rating (1-5 stars) | Rating selected | | |
| 5 | Enter feedback text | Feedback entered | | |
| 6 | Click "Submit Feedback" | Feedback submitted | | |
| 7 | Verify is_feedback_submitted = true | Flag updated | | |
| 8 | Verify feedback_submitted_at recorded | Timestamp saved | | |

---

## Test Case 14.2: Cannot Submit Feedback on Unresolved Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to a pending/processing concern | Concern displayed | | |
| 3 | Check for feedback form | Feedback form NOT available | | |
| 4 | Verify message | "Feedback available after resolution" or form hidden | | |

---

## Test Case 14.3: Cannot Submit Feedback Twice

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to a concern with feedback already submitted | Concern displayed | | |
| 3 | Check feedback section | Shows "Feedback submitted" or disabled | | |
| 4 | Verify cannot modify | Form not editable | | |

---

# MODULE 15: CONCERN TIMELINE AND HISTORY

## Test Case 15.1: View Concern Timeline

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to a concern | Concern details displayed | | |
| 3 | Click "View Timeline" | Timeline page displayed | | |
| 4 | Verify submission event | "Concern submitted" entry visible | | |
| 5 | Verify status changes | All status updates in timeline | | |
| 6 | Verify timestamps | Dates/times visible for each event | | |

---

## Test Case 15.2: Download Concern Timeline as PDF

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to concern timeline | Timeline displayed | | |
| 3 | Click "Download PDF" button | PDF generation started | | |
| 4 | Verify PDF downloads | File downloaded | | |
| 5 | Open and verify PDF content | Timeline data in PDF | | |

---

## Test Case 15.3: Export Concern History

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to concern history | History page displayed | | |
| 3 | Click "Export History" | Export initiated | | |
| 4 | Select format | Format selected | | |
| 5 | Verify file downloads | History exported | | |

---

# MODULE 16: REMINDERS

## Test Case 16.1: Student View Reminders

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Navigate to "Reminders" section | Reminders page displayed | | |
| 3 | Verify reminder list | Reminders visible | | |
| 4 | Verify deadline-related reminders | 3-day and 5-day reminders shown | | |

---

## Test Case 16.2: Check Reminders Automatically

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Submit a concern with 3-day deadline | Concern created | | |
| 2 | When deadline approaches (day 3) | System checks reminders | | |
| 3 | Verify reminder notification created | "reminder_3_days" notification sent | | |
| 4 | When day 5 reached | System checks again | | |
| 5 | Verify 5-day reminder | "reminder_5_days" notification sent | | |

---

# MODULE 17: ONLINE STATUS

## Test Case 17.1: Update Online Status on Login

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Login successful | | |
| 2 | Verify is_online = true | Student marked online | | |
| 3 | Verify last_seen updated | Timestamp recorded | | |
| 4 | Check SSC/Admin view | Student shows as "Online" | | |

---

## Test Case 17.2: Set Offline on Logout

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Click Logout | Logout processed | | |
| 3 | Verify is_online = false | Student marked offline | | |
| 4 | Verify last_seen updated | Timestamp recorded | | |

---

## Test Case 17.3: Get Students Online Status

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC/Admin | Dashboard displayed | | |
| 2 | View students list | Students displayed | | |
| 3 | Verify online indicators | Green/gray badges for status | | |
| 4 | Verify status is real-time | Status updates when students login/logout | | |

---

# MODULE 18: CHATBOT/AI ANALYSIS

## Test Case 18.1: Analyze Concern with AI Chatbot

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to concern submission | Form displayed | | |
| 3 | Enter concern description | Text entered | | |
| 4 | Click "Analyze with AI" button | AI analysis initiated | | |
| 5 | Verify AI suggestions displayed | Concern type/priority suggestions shown | | |
| 6 | Verify suggestions can be applied | Can accept AI recommendations | | |

---

# MODULE 19: ACCESS CONTROL

## Test Case 19.1: Student Cannot Access Admin Pages

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Manually navigate to /admin_dashboard | Access denied | | |
| 3 | Verify error message | "You do not have permission" or redirect | | |
| 4 | Verify redirect to appropriate page | Redirected to login or student dashboard | | |

---

## Test Case 19.2: Student Cannot Access SSC Pages

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Student dashboard displayed | | |
| 2 | Manually navigate to /ssc_dashboard | Access denied | | |
| 3 | Verify error message | Permission error displayed | | |

---

## Test Case 19.3: SSC Cannot Access Admin Pages

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as SSC staff | SSC dashboard displayed | | |
| 2 | Manually navigate to /admin/user_approval | Access denied | | |
| 3 | Verify error message | "Required role: admin" or similar | | |

---

## Test Case 19.4: Unauthenticated User Access Protection

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Open browser without logging in | No session exists | | |
| 2 | Navigate directly to /student_dashboard | Access denied | | |
| 3 | Verify redirect to login | Login page displayed | | |
| 4 | Verify flash message | "Please log in to access this page" | | |

---

# MODULE 20: FILE DOWNLOADS

## Test Case 20.1: Download Concern Attachment

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student/SSC/Admin | Dashboard displayed | | |
| 2 | Navigate to concern with attachments | Attachments listed | | |
| 3 | Click download link on attachment | Download initiated | | |
| 4 | Verify file downloads | File saved to device | | |
| 5 | Verify file is correct | Content matches uploaded file | | |

---

## Test Case 20.2: Download Chat Attachment

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as user | Dashboard displayed | | |
| 2 | Navigate to message with attachment | Chat message visible | | |
| 3 | Click download link | Download initiated | | |
| 4 | Verify file downloads | File saved | | |

---

## Test Case 20.3: Remove Attachment from Concern

| Step No. | Step Details | Expected Result | Actual Result | Status |
|----------|--------------|-----------------|---------------|--------|
| 1 | Login as student | Dashboard displayed | | |
| 2 | Navigate to own pending concern with attachments | Attachments visible | | |
| 3 | Click "Remove" on an attachment | Confirmation displayed | | |
| 4 | Confirm removal | Attachment deleted | | |
| 5 | Verify attachment removed from database | Not in attachments list | | |
| 6 | Verify file deleted from uploads folder | File removed from server | | |

---

# SUMMARY

| Module | Total Test Cases | Pass | Fail | Not Tested |
|--------|------------------|------|------|------------|
| 1. User Authentication | 7 | | | |
| 2. User Registration | 8 | | | |
| 3. Password Recovery | 3 | | | |
| 4. Student Concern Submission | 8 | | | |
| 5. Concern Management (SSC) | 8 | | | |
| 6. Concern Management (Admin) | 5 | | | |
| 7. User Management (Admin) | 6 | | | |
| 8. Department & Course Management | 8 | | | |
| 9. Concern Types Management | 3 | | | |
| 10. Notifications | 6 | | | |
| 11. Messaging/Chat | 4 | | | |
| 12. Profile Management | 3 | | | |
| 13. Analytics & Reports | 4 | | | |
| 14. Student Concern Feedback | 3 | | | |
| 15. Concern Timeline & History | 3 | | | |
| 16. Reminders | 2 | | | |
| 17. Online Status | 3 | | | |
| 18. Chatbot/AI Analysis | 1 | | | |
| 19. Access Control | 4 | | | |
| 20. File Downloads | 3 | | | |
| **TOTAL** | **92** | | | |

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Tester | | | |
| Developer | | | |
| Project Manager | | | |

---

*Document Version: 1.0*
*Last Updated: February 2026*
