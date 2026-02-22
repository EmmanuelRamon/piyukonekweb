# Paano i-Test ang System Nang Hindi Pa Naka-Host (Local Testing)

Para ma-test na **sabay-sabay** ang login ng **student, guidance (SSC), at admin**, gawin ang mga hakbang sa baba sa computer mo. Walang kailangang i-host; local lang.

---

## 1. Ihanda ang database at .env

- May **MySQL** na naka-install at may database na **piyukonek** (o kung ano ang nakalagay sa `DATABASE_URL`).
- May **.env** file (copy from `.env.example`) na may tamang `DATABASE_URL`, `SECRET_KEY`, at kung gusto mo ng email, `MAIL_*`.

---

## 2. Patakbuhin ang app sa computer mo

Sa terminal/command prompt, pumunta sa folder ng project at i-run ang app.

**Kung nasa folder `Richwell` ka (root ng project):**
```bash
cd "c:\Users\Admin\Desktop\4TH YEAR\FOR FOD SYSTEM\Richwell\piyukonek"
python app.py
```

**O kung nasa `piyukonek` ka na:**
```bash
python app.py
```

Dapat may lumabas na tulad ng:
```text
 * Running on http://127.0.0.1:5000
```

Huwag isara ang terminal; iwanan mong tumatakbo ang app.

---

## 3. Test na sabay-sabay ang login (Student, SSC, Admin)

Ang bawat **browser** o **incognito window** ay may sariling session (parang ibang user). Gamitin mo yan para mag-login nang sabay ang tatlong role.

### Paraan A: Isang PC – iba’t ibang browser / incognito

1. **Browser 1 (hal. Chrome)**  
   - Buksan: **http://127.0.0.1:5000**  
   - Login bilang **Student** (gamit existing student account).

2. **Browser 2 (hal. Edge, Firefox, o Chrome Incognito)**  
   - Buksan ulit: **http://127.0.0.1:5000**  
   - Login bilang **SSC / Guidance** (existing SSC account).

3. **Browser 3 (hal. another Incognito o ibang browser)**  
   - Buksan ulit: **http://127.0.0.1:5000**  
   - Login bilang **Admin** (existing admin account).

**Dapat:**  
- Lahat naka-login nang sabay.  
- Bawat isa nakikita ang sariling dashboard (student → student, SSC → SSC, admin → admin).  
- Walang na-lo-logout ang isa kapag nag-login ang iba.

### Paraan B: Iba’t ibang device (same WiFi)

Kung gusto mo i-test mula sa **phone** o **ibang laptop** (parang talagang ibang user):

1. Sa `app.py`, gawing tumakbo sa lahat ng network interface. Hanapin ang linyang:
   ```python
   app.run(debug=debug_mode)
   ```
   Palitan ng:
   ```python
   app.run(debug=debug_mode, host='0.0.0.0', port=5000)
   ```
2. Alamin ang **local IP** ng PC mo (hal. `ipconfig` sa Windows → IPv4, e.g. `192.168.1.10`).
3. Sa other device, sa browser i-type: **http://192.168.1.10:5000** (palitan ng tunay na IP).
4. Doon mag-login ng isang role (e.g. student). Sa PC mo, mag-login sa Chrome ng admin at sa Edge ng SSC — sabay na tatlong user.

---

## 4. Ano dapat i-check

| Test | Inaasahan |
|------|-----------|
| Student naka-login | Student dashboard at student pages lang. |
| SSC naka-login (sabay) | SSC dashboard at SSC pages; hindi naaapektuhan student. |
| Admin naka-login (sabay) | Admin dashboard at admin pages; hindi naaapektuhan student at SSC. |
| Mag-logout ang isa | Yung isang user lang ang na-logout; yung dalawa naka-login pa rin. |

Kung ganito ang nangyayari, kapag na-host na (e.g. Railway), **ganoon din ang behavior** — pwede sabay-sabay mag-login ang student, guidance, at admin.

---

## 5. Kung wala ka pang test accounts

- **Student:** Mag-sign up sa “Student” signup flow, tapos verify (OTP kung naka-setup ang email; kung local lang, baka naka-print sa console ang OTP o may bypass).
- **SSC / Admin:** Kung may seed script o admin panel para mag-add ng user, gumawa ng isang SSC at isang Admin account. Kung wala, kailangan mo muna mag-create sa database o magdagdag ng simple “create test user” route para sa local testing.

---

## Quick checklist

1. MySQL running, database created, `.env` set.
2. `python app.py` sa `piyukonek` folder; nakikita ang http://127.0.0.1:5000.
3. Buksan 3 browser/incognito → login bilang Student, SSC, Admin nang sabay.
4. I-check na lahat naka-login at tama ang dashboard bawat isa.

Pag na-verify mo na sa local na sabay-sabay silang pwedeng naka-login, pareho na rin ang mangyayari kapag naka-host na ang system.
