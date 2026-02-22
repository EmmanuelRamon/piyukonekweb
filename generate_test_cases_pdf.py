from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_test_cases_pdf():
    # Create PDF document
    doc = SimpleDocTemplate(
        "TEST_CASES_SCENARIOS.pdf",
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        alignment=TA_LEFT
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    # ==================== STUDENTS' TEST CASE SCENARIO ====================
    elements.append(Paragraph("STUDENTS' TEST CASE SCENARIO", title_style))
    
    student_data = [
        # Header row
        [
            Paragraph("<b>STEP NO.</b>", header_style),
            Paragraph("<b>STEP DETAILS</b>", header_style),
            Paragraph("<b>EXPECTED RESULTS</b>", header_style),
            Paragraph("<b>ACTUAL RESULTS</b>", header_style),
            Paragraph("<b>STATUS</b>", header_style),
            ""
        ],
        # Sub-header for Status
        ["", "", "", "", Paragraph("<b>PASS</b>", header_style), Paragraph("<b>FAIL</b>", header_style)],
        
        # Test cases
        [
            "1.",
            Paragraph("Go to Login, then \"Student Signup\" if new; verify OTP if required.", cell_style),
            Paragraph("Student account created and verified.", cell_style),
            "",
            "",
            ""
        ],
        [
            "2.",
            Paragraph("Log in with email/ID and password.", cell_style),
            Paragraph("Student successfully logged in.", cell_style),
            "",
            "",
            ""
        ],
        [
            "3.",
            Paragraph("Go to Dashboard, then view stats: total/pending/resolved concerns.", cell_style),
            Paragraph("Students sees overall status of concerns.", cell_style),
            "",
            "",
            ""
        ],
        [
            "4.",
            Paragraph("See recent concerns list and open any item for details.", cell_style),
            Paragraph("Students views details of concerns.", cell_style),
            "",
            "",
            ""
        ],
        [
            "5.",
            Paragraph("Go to Dashboard, then \"Raise a Concern\" or Students, then \"My Concerns\".", cell_style),
            Paragraph("Concern form opens.", cell_style),
            "",
            "",
            ""
        ],
        [
            "6.",
            Paragraph("Fill: Type, Title, Details, Priority.", cell_style),
            Paragraph("Concern details entered.", cell_style),
            "",
            "",
            ""
        ],
        [
            "7.",
            Paragraph("Attach up to 3 files (PDF/DOC/IMG/TXT, less than 10MB each), preview/remove if needed.", cell_style),
            Paragraph("Files successfully uploaded.", cell_style),
            "",
            "",
            ""
        ],
        [
            "8.",
            Paragraph("Click Submit. If the concern limit is reached, wait for pending ones to resolve.", cell_style),
            Paragraph("Concern submitted or notice given if limit reached.", cell_style),
            "",
            "",
            ""
        ],
        [
            "9.",
            Paragraph("Click \"My Concerns\": sort by Newest/Oldest.", cell_style),
            Paragraph("Concerns are sorted as selected.", cell_style),
            "",
            "",
            ""
        ],
        [
            "10.",
            Paragraph("For \"Pending\" concerns, click Edit to update Type, Title, Details, or attachments, then Save.", cell_style),
            Paragraph("Concern updated successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "11.",
            Paragraph("Open any concern to see full details: Type, Title, Description, Priority, Status, Attachments, Response, Timeline.", cell_style),
            Paragraph("All concern details displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "12.",
            Paragraph("For resolved concerns, rate (1-5 stars) and provide feedback, then submit.", cell_style),
            Paragraph("Feedback submitted successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "13.",
            Paragraph("View concern timeline showing all status changes and actions.", cell_style),
            Paragraph("Timeline displayed with history.", cell_style),
            "",
            "",
            ""
        ],
        [
            "14.",
            Paragraph("Click Notifications icon to view all notifications.", cell_style),
            Paragraph("Notifications list displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "15.",
            Paragraph("Click a notification to mark as read; use \"Mark All Read\" or \"Delete All\".", cell_style),
            Paragraph("Notifications marked/deleted.", cell_style),
            "",
            "",
            ""
        ],
        [
            "16.",
            Paragraph("Go to Messages to chat with SSC/Admin; send text or attachments.", cell_style),
            Paragraph("Messages sent and received.", cell_style),
            "",
            "",
            ""
        ],
        [
            "17.",
            Paragraph("Go to Profile to view/update profile image.", cell_style),
            Paragraph("Profile updated successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "18.",
            Paragraph("Click Logout to end session.", cell_style),
            Paragraph("User logged out, redirected to login.", cell_style),
            "",
            "",
            ""
        ],
        [
            "19.",
            Paragraph("On Login page, click \"Forgot Password\", enter email, receive reset link, set new password.", cell_style),
            Paragraph("Password reset successful.", cell_style),
            "",
            "",
            ""
        ],
        [
            "20.",
            Paragraph("Leave session idle for 30+ minutes, then try any action.", cell_style),
            Paragraph("Session expired, redirected to login.", cell_style),
            "",
            "",
            ""
        ],
    ]
    
    # Create table with column widths
    col_widths = [0.6*inch, 3.2*inch, 2.5*inch, 1.8*inch, 0.7*inch, 0.7*inch]
    student_table = Table(student_data, colWidths=col_widths, repeatRows=2)
    
    # Table styling
    student_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Merge STATUS header
        ('SPAN', (4, 0), (5, 0)),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Data rows
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (-1, -1), 9),
        ('ALIGN', (0, 2), (0, -1), 'CENTER'),
        ('ALIGN', (4, 2), (5, -1), 'CENTER'),
        
        # Row padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(student_table)
    elements.append(PageBreak())
    
    # ==================== SSC/GUIDANCE TEST CASE SCENARIO ====================
    elements.append(Paragraph("SSC/GUIDANCE TEST CASE SCENARIO", title_style))
    
    ssc_data = [
        # Header row
        [
            Paragraph("<b>STEP NO.</b>", header_style),
            Paragraph("<b>STEP DETAILS</b>", header_style),
            Paragraph("<b>EXPECTED RESULTS</b>", header_style),
            Paragraph("<b>ACTUAL RESULTS</b>", header_style),
            Paragraph("<b>STATUS</b>", header_style),
            ""
        ],
        # Sub-header for Status
        ["", "", "", "", Paragraph("<b>PASS</b>", header_style), Paragraph("<b>FAIL</b>", header_style)],
        
        # Test cases
        [
            "1.",
            Paragraph("Go to Login, then \"SSC Signup\" if new; verify OTP if required.", cell_style),
            Paragraph("SSC account created (pending admin approval).", cell_style),
            "",
            "",
            ""
        ],
        [
            "2.",
            Paragraph("Log in with username and password after admin approval.", cell_style),
            Paragraph("SSC successfully logged in.", cell_style),
            "",
            "",
            ""
        ],
        [
            "3.",
            Paragraph("View Dashboard: total concerns, pending, processing, resolved counts.", cell_style),
            Paragraph("Dashboard statistics displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "4.",
            Paragraph("Go to Concerns list; filter by status, type, or priority.", cell_style),
            Paragraph("Concerns filtered as selected.", cell_style),
            "",
            "",
            ""
        ],
        [
            "5.",
            Paragraph("Search for specific concern by title or student name.", cell_style),
            Paragraph("Search results displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "6.",
            Paragraph("Click on a concern to view full details including attachments.", cell_style),
            Paragraph("Concern details displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "7.",
            Paragraph("Update concern priority level (Low/Medium/High/Urgent).", cell_style),
            Paragraph("Priority updated, student notified.", cell_style),
            "",
            "",
            ""
        ],
        [
            "8.",
            Paragraph("Enter response notes and optional attachment, click Submit Response.", cell_style),
            Paragraph("Response saved, status changed to Processing.", cell_style),
            "",
            "",
            ""
        ],
        [
            "9.",
            Paragraph("Click \"Mark as Resolved\" with resolution notes.", cell_style),
            Paragraph("Concern marked as Resolved, student notified.", cell_style),
            "",
            "",
            ""
        ],
        [
            "10.",
            Paragraph("Select multiple concerns using checkboxes for bulk actions.", cell_style),
            Paragraph("Multiple concerns selected.", cell_style),
            "",
            "",
            ""
        ],
        [
            "11.",
            Paragraph("Apply bulk status update (Processing/Resolved/Closed).", cell_style),
            Paragraph("All selected concerns updated.", cell_style),
            "",
            "",
            ""
        ],
        [
            "12.",
            Paragraph("Bulk assign selected concerns to specific SSC staff member.", cell_style),
            Paragraph("Concerns assigned to selected staff.", cell_style),
            "",
            "",
            ""
        ],
        [
            "13.",
            Paragraph("Bulk export selected concerns to CSV or PDF.", cell_style),
            Paragraph("Export file downloaded.", cell_style),
            "",
            "",
            ""
        ],
        [
            "14.",
            Paragraph("Go to Students section to view all registered students.", cell_style),
            Paragraph("Students list displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "15.",
            Paragraph("Click student name to view their concern history.", cell_style),
            Paragraph("Student's concerns displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "16.",
            Paragraph("Go to Concern Types to add/archive concern categories.", cell_style),
            Paragraph("Concern types managed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "17.",
            Paragraph("View Notifications for new concerns and updates.", cell_style),
            Paragraph("Notifications displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "18.",
            Paragraph("Go to Messages to communicate with students.", cell_style),
            Paragraph("Chat interface displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "19.",
            Paragraph("Go to Analytics to view concern statistics and charts.", cell_style),
            Paragraph("Analytics dashboard displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "20.",
            Paragraph("Export analytics report to PDF/CSV.", cell_style),
            Paragraph("Report downloaded.", cell_style),
            "",
            "",
            ""
        ],
        [
            "21.",
            Paragraph("Go to Profile to update profile image.", cell_style),
            Paragraph("Profile updated successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "22.",
            Paragraph("Click Logout to end session.", cell_style),
            Paragraph("User logged out.", cell_style),
            "",
            "",
            ""
        ],
    ]
    
    ssc_table = Table(ssc_data, colWidths=col_widths, repeatRows=2)
    ssc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (4, 0), (5, 0)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (-1, -1), 9),
        ('ALIGN', (0, 2), (0, -1), 'CENTER'),
        ('ALIGN', (4, 2), (5, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(ssc_table)
    elements.append(PageBreak())
    
    # ==================== ADMIN TEST CASE SCENARIO ====================
    elements.append(Paragraph("ADMIN TEST CASE SCENARIO", title_style))
    
    admin_data = [
        # Header row
        [
            Paragraph("<b>STEP NO.</b>", header_style),
            Paragraph("<b>STEP DETAILS</b>", header_style),
            Paragraph("<b>EXPECTED RESULTS</b>", header_style),
            Paragraph("<b>ACTUAL RESULTS</b>", header_style),
            Paragraph("<b>STATUS</b>", header_style),
            ""
        ],
        # Sub-header for Status
        ["", "", "", "", Paragraph("<b>PASS</b>", header_style), Paragraph("<b>FAIL</b>", header_style)],
        
        # Test cases
        [
            "1.",
            Paragraph("Go to Login, then \"Admin Signup\" if new; verify OTP if required.", cell_style),
            Paragraph("Admin account created.", cell_style),
            "",
            "",
            ""
        ],
        [
            "2.",
            Paragraph("Log in with username and password.", cell_style),
            Paragraph("Admin successfully logged in.", cell_style),
            "",
            "",
            ""
        ],
        [
            "3.",
            Paragraph("View Dashboard: total users, concerns summary, recent activities.", cell_style),
            Paragraph("Dashboard statistics displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "4.",
            Paragraph("Go to User Approval to view pending student/SSC registrations.", cell_style),
            Paragraph("Pending users listed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "5.",
            Paragraph("Click \"Approve\" on a pending student account.", cell_style),
            Paragraph("Student approved, status changed to active.", cell_style),
            "",
            "",
            ""
        ],
        [
            "6.",
            Paragraph("Click \"Reject\" on a pending student account.", cell_style),
            Paragraph("Student rejected/removed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "7.",
            Paragraph("Approve or Reject pending SSC staff accounts.", cell_style),
            Paragraph("SSC account status updated.", cell_style),
            "",
            "",
            ""
        ],
        [
            "8.",
            Paragraph("Go to User Management to view all users (Students, SSC).", cell_style),
            Paragraph("All users listed with details.", cell_style),
            "",
            "",
            ""
        ],
        [
            "9.",
            Paragraph("Go to Concerns to view all submitted concerns.", cell_style),
            Paragraph("All concerns displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "10.",
            Paragraph("Click on a concern to view full details.", cell_style),
            Paragraph("Concern details displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "11.",
            Paragraph("Enter response notes with optional attachment, click Submit Response.", cell_style),
            Paragraph("Admin response saved.", cell_style),
            "",
            "",
            ""
        ],
        [
            "12.",
            Paragraph("Update existing response if needed.", cell_style),
            Paragraph("Response updated successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "13.",
            Paragraph("Click \"Reject Concern\" with rejection reason.", cell_style),
            Paragraph("Concern rejected, student notified.", cell_style),
            "",
            "",
            ""
        ],
        [
            "14.",
            Paragraph("Export individual concern to PDF.", cell_style),
            Paragraph("PDF downloaded with concern details.", cell_style),
            "",
            "",
            ""
        ],
        [
            "15.",
            Paragraph("Export all concerns to PDF.", cell_style),
            Paragraph("PDF report downloaded.", cell_style),
            "",
            "",
            ""
        ],
        [
            "16.",
            Paragraph("Go to Departments to view all departments.", cell_style),
            Paragraph("Departments list displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "17.",
            Paragraph("Add new department with name, code, and description.", cell_style),
            Paragraph("Department created successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "18.",
            Paragraph("Edit existing department details.", cell_style),
            Paragraph("Department updated.", cell_style),
            "",
            "",
            ""
        ],
        [
            "19.",
            Paragraph("Archive a department; verify it's hidden from registration.", cell_style),
            Paragraph("Department archived.", cell_style),
            "",
            "",
            ""
        ],
        [
            "20.",
            Paragraph("Restore an archived department.", cell_style),
            Paragraph("Department restored to active.", cell_style),
            "",
            "",
            ""
        ],
        [
            "21.",
            Paragraph("Go to Courses to view all courses.", cell_style),
            Paragraph("Courses list displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "22.",
            Paragraph("Add new course under a department.", cell_style),
            Paragraph("Course created successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "23.",
            Paragraph("Edit existing course details.", cell_style),
            Paragraph("Course updated.", cell_style),
            "",
            "",
            ""
        ],
        [
            "24.",
            Paragraph("Archive and restore courses.", cell_style),
            Paragraph("Course archive/restore works.", cell_style),
            "",
            "",
            ""
        ],
        [
            "25.",
            Paragraph("Go to Concern Types to manage categories.", cell_style),
            Paragraph("Concern types displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "26.",
            Paragraph("Add new concern type.", cell_style),
            Paragraph("Type created successfully.", cell_style),
            "",
            "",
            ""
        ],
        [
            "27.",
            Paragraph("View Notifications for system alerts and new concerns.", cell_style),
            Paragraph("Notifications displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "28.",
            Paragraph("Go to Activities to view system activity logs.", cell_style),
            Paragraph("Activities log displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "29.",
            Paragraph("Go to Analytics to view comprehensive statistics.", cell_style),
            Paragraph("Analytics dashboard displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "30.",
            Paragraph("Export analytics to CSV/PDF.", cell_style),
            Paragraph("Analytics report downloaded.", cell_style),
            "",
            "",
            ""
        ],
        [
            "31.",
            Paragraph("Go to Messages to communicate with students/SSC.", cell_style),
            Paragraph("Messaging interface displayed.", cell_style),
            "",
            "",
            ""
        ],
        [
            "32.",
            Paragraph("Update admin profile image.", cell_style),
            Paragraph("Profile image updated.", cell_style),
            "",
            "",
            ""
        ],
        [
            "33.",
            Paragraph("Click Logout to end session.", cell_style),
            Paragraph("Admin logged out.", cell_style),
            "",
            "",
            ""
        ],
    ]
    
    admin_table = Table(admin_data, colWidths=col_widths, repeatRows=2)
    admin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (4, 0), (5, 0)),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 2), (-1, -1), 9),
        ('ALIGN', (0, 2), (0, -1), 'CENTER'),
        ('ALIGN', (4, 2), (5, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    elements.append(admin_table)
    
    # Build PDF
    doc.build(elements)
    print("PDF generated successfully: TEST_CASES_SCENARIOS.pdf")

if __name__ == "__main__":
    create_test_cases_pdf()
