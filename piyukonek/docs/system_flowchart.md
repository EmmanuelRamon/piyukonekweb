## PIYUKONEK System Flowcharts

Below are Mermaid flowcharts covering the overall system and the core user flows. You can preview these directly in many Markdown viewers that support Mermaid (e.g., GitHub, VS Code with Mermaid extension).

### Overall System (High-Level)
```mermaid
flowchart TD
  subgraph Client[Web Client (Browser)]
    UI[HTML/CSS/JS Templates] -->|Forms/Clicks| SM[session_manager.js]
  end

  SM -->|HTTP(S) Requests| FL[Flask App (piyukonek/app.py)]
  FL --> RT[Route Handlers / Controllers]
  RT --> SV[Services / Business Logic]
  SV --> DB[(SQLite DB: instance/piyukonek.db)]
  SV --> FS[(File Storage: uploads/)]

  subgraph Roles
    A[Admin]
    S[Student]
    SSC[SSC]
  end

  A --- UI
  S --- UI
  SSC --- UI

  DB <-. migrations .-> MIG[Migration Scripts (SQL/Python)]
```

### Authentication & Account Management
```mermaid
flowchart LR
  L[Open Login/Signup Page] --> C{Choose Action}
  C -->|Login| LG[Submit Credentials]
  C -->|Signup| SU[Submit Registration]

  LG --> V{Validate Credentials}
  V -->|Valid| RDR[Redirect based on role]
  V -->|Invalid| ERR[Show error]

  SU --> VR{Validate Fields}
  VR -->|Student| PEND1[Create Pending Account]
  VR -->|SSC| PEND2[Create Pending Account]
  VR -->|Admin| PEND3[Create Pending Account]

  PEND1 --> APRVQ[Await Admin Approval / OTP if enabled]
  PEND2 --> APRVQ
  PEND3 --> APRVQ

  APRVQ -->|Approved| RDR
  APRVQ -->|Rejected| RJ[Notify Rejection]

  RDR -->|Student| SD[s t u d e n t _ d a s h b o a r d]
  RDR -->|SSC| SSCD[ssc_dashboard]
  RDR -->|Admin| AD[admin_dashboard]
```

### Student Concern Lifecycle
```mermaid
flowchart TD
  S0[Student: Open concern page] --> S1[Create Concern (title, desc, type, priority,...)]
  S1 --> S2[Attach files (uploads/)]
  S2 --> S3[Submit]
  S3 --> B1[Backend validates & saves]
  B1 --> DB[(DB)]
  B1 --> TL[Initialize Timeline/Status]
  TL --> N1[Notify SSC/Admin as configured]

  N1 --> SSCV[SSC Views concern list]
  S3 --> STV[Student views concern_timeline]

  subgraph Updates
    SSCV --> ACT[SSC adds update / request info / set deadline]
    ACT --> DB
    ACT --> TL
    TL --> N2[Notify Student]
    N2 --> STV
  end

  subgraph Resolution
    ACT --> RES{Resolved?}
    RES -->|Yes| C1[Mark resolved/closed]
    C1 --> FB[Collect rating/feedback]
    FB --> DB
    RES -->|No| Loop[Continue updates]
    Loop --> SSCV
  end
```

### SSC Handling Flow
```mermaid
flowchart LR
  O[SSC opens ssc_concern] --> F[Filter/Sort/Priority queues]
  F --> V[Open ssc_concern_detail]
  V --> A1[Add notes/update status]
  V --> A2[Request additional info]
  V --> A3[Set/Update deadline]
  A1 --> DB[(DB)]
  A2 --> N[Notify Student]
  A3 --> DB
  A3 --> N
  A1 --> N
  V --> CHK{Issue resolved?}
  CHK -->|Yes| CLOSE[Close Concern]
  CLOSE --> FBQ[Trigger feedback request]
  FBQ --> DB
  CHK -->|No| O
```

### Admin Oversight & Management
```mermaid
flowchart TD
  AD[Admin Dashboard] --> UMG[user_management]
  AD --> APR[user_approval]
  AD --> AN[admin_analytics]
  AD --> CN[admin_concern overview/detail]
  AD --> MSG[admin_messages]

  UMG -->|Activate/Deactivate| DB
  APR -->|Approve/Reject| DB
  CN -->|Escalate/Assign/Update| DB
  MSG -->|Send announcements| Notif[Notifications]
  AN -->|View KPIs| VIS[Charts/Tables]
```

### Notifications & Messaging
```mermaid
flowchart LR
  EVT[System Events: new concern, update, deadline, approval] --> NT[Create Notification]
  NT --> DB[(DB)]
  DB --> UI[Notifications UI (per role)]
  UI --> READ[Mark as read]
  READ --> DB
```

### Data Storage
```mermaid
flowchart LR
  SQ[(SQLite: instance/piyukonek.db)] <---> APP[Flask App]
  FS[(uploads/ directory)] <---> APP
  MIG[SQL/Python migrations] --> SQ
```

Notes
- These diagrams reflect the repository structure: Flask backend, role-based templates, SQLite database in `instance/`, and file uploads in `uploads/`.
- If OTP or email is used for verification, place those steps between registration and approval in the Auth flow.
- Adjust names (e.g., route titles) if UI labels differ in your templates.


