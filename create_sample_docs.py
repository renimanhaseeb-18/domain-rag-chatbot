# Creates two fictional company PDFs (Policy.pdf and Handbook.pdf) for testing the RAG chatbot.
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

POLICY = [
("1. Introduction and Scope", [
 "This Company Policy document applies to all employees, contractors and interns of Nova Tech Solutions Pvt. Ltd. It explains the rules of conduct, working arrangements, leave, security and expenses that every person must follow.",
 "The policy is effective from 1 January 2026 and is reviewed once every year by the Human Resources (HR) department. Employees will be informed by email about any change at least 15 days before it takes effect."]),
("2. Code of Conduct", [
 "All employees must treat colleagues, customers and partners with respect. Harassment, discrimination and bullying of any kind are strictly prohibited and will lead to disciplinary action.",
 "Any conflict of interest, such as a family member working for a competitor, must be disclosed to HR within 7 days. Gifts from customers or vendors worth more than Rs. 2,000 must be reported to the manager and cannot be kept without written approval."]),
("3. Working Hours", [
 "The standard working hours are 9:30 AM to 6:30 PM, Monday to Friday, with a one-hour lunch break. Employees may use flexible timing and start between 8:30 AM and 10:30 AM, as long as they complete their daily hours.",
 "Core hours are 11:00 AM to 4:00 PM, during which every employee must be available for meetings. Overtime must be approved in advance by the reporting manager and is compensated with a compensatory off day, not with cash."]),
("4. Remote Work Policy", [
 "Employees who have completed their probation period may work remotely for up to 2 days per week. Remote work needs prior approval from the reporting manager and must be recorded in the HR portal.",
 "While working remotely, employees must connect through the company VPN and be reachable during core hours. A monthly internet allowance of Rs. 1,000 is paid to employees who work remotely at least 4 days a month."]),
("5. Data Security", [
 "Passwords must be at least 12 characters long and must be changed every 90 days. Multi-factor authentication (MFA) is mandatory for email, the VPN and all cloud tools.",
 "Confidential company data must never be copied to personal USB drives or personal email accounts. Any suspected security incident, such as a lost laptop or a phishing email, must be reported to the security team at security@novatech.example within 24 hours."]),
("6. Leave Policy", [
 "Every full-time employee receives 18 days of paid annual leave per year, 10 days of sick leave per year and 6 days of casual leave per year. Annual leave should be applied for at least 5 working days in advance. A medical certificate is required when sick leave lasts more than 2 consecutive days.",
 "Unused annual leave can be carried forward to the next year up to a maximum of 10 days. Maternity leave is 26 weeks and paternity leave is 10 working days. Leave without pay needs written approval from the manager and HR."]),
("7. Expense Reimbursement", [
 "Employees must submit expense claims within 30 days of the expense through the finance portal. Receipts are required for every expense above Rs. 500.",
 "During official travel, the daily meal allowance is Rs. 800 and travel must be booked in economy class. Approved claims are reimbursed within 15 working days of submission."]),
("8. Disciplinary and Grievance Procedure", [
 "Violations of company policy are handled in four steps: a verbal warning, a written warning, a final written warning and, if the behaviour continues, termination of employment. Serious misconduct may lead to immediate termination.",
 "Employees can raise a grievance with HR within 15 days of the incident. HR will resolve the grievance within 21 days. Complaints about harassment are handled by the Internal Complaints Committee."]),
]

HANDBOOK = [
("1. Welcome to Nova Tech", [
 "Nova Tech Solutions was founded in 2015 and is headquartered in Bengaluru, with offices in Pune and Hyderabad. The company has about 450 employees and builds software and data products for customers in banking, retail and healthcare.",
 "Our values are customer first, integrity, ownership and continuous learning. This handbook explains what you can expect from the company and what the company expects from you."]),
("2. Departments and Teams", [
 "Nova Tech has six departments: Engineering, Data and AI, Product, Human Resources, Finance and Sales. Each department is led by a Vice President who reports to the leadership team.",
 "Every employee belongs to a team of 6 to 10 people led by a team lead. Team leads hold a weekly planning meeting every Monday at 10:30 AM."]),
("3. Onboarding", [
 "On the first day, new joiners attend an orientation at the HR desk at 10:00 AM. An employee ID card is issued within 2 working days of joining.",
 "Each new employee is assigned a buddy for the first 30 days. The mandatory information security training must be completed in the first week."]),
("4. Probation and Confirmation", [
 "The probation period is 6 months from the date of joining. At the end of probation the manager and HR review performance and confirm the employee in writing.",
 "The notice period during probation is 15 days. After confirmation the notice period is 60 days for all employees."]),
("5. Performance Reviews", [
 "Performance is reviewed twice a year. The main annual appraisal takes place in April and a mid-year check-in takes place in October. Ratings use a scale of 1 to 5.",
 "Employees with a rating of 4 or above are considered for promotion. Salary increments are decided after the April appraisal."]),
("6. Training and Learning", [
 "Every employee gets a learning budget of Rs. 25,000 per year for courses, books and conferences, and is expected to complete at least 40 hours of learning each year.",
 "The fee for a professional certification exam is reimbursed after the employee passes. Internal tech talks are held every Friday at 4:00 PM."]),
("7. Compensation and Benefits", [
 "The company contributes 12% of basic salary to the Provident Fund. An annual performance bonus of up to 10% of annual salary is paid based on the April rating.",
 "Meal coupons worth Rs. 2,200 per month are provided. Employees who refer a successful candidate receive a referral bonus of Rs. 30,000 once the new hire completes 3 months."]),
("8. Health Insurance", [
 "Every employee is covered by a group health insurance policy of Rs. 5 lakh from the first day of employment. The cover includes the employee, spouse and up to 2 children. Parents can be added by paying an additional premium.",
 "Cashless treatment is available at network hospitals. Each employee is also eligible for one free annual health check-up."]),
("9. Office Facilities", [
 "The cafeteria is open from 12:00 PM to 3:00 PM. A shuttle service runs from 7:00 AM to 9:00 PM on 4 routes across the city.",
 "Meeting rooms can be booked through the calendar tool. The office also has a gym, a quiet room and free parking for two-wheelers."]),
("10. IT Equipment", [
 "A laptop is issued to every employee on joining and is replaced after 3 years of use. Employees must not install unlicensed or personal software on company laptops.",
 "A lost or damaged device must be reported to the IT helpdesk within 48 hours. All equipment must be returned on the last working day."]),
("11. Attendance", [
 "Attendance is recorded by biometric swipe at the office entrance. A full working day requires at least 8 hours of logged time and a half day requires at least 4 hours.",
 "A late arrival is any swipe after 10:30 AM. Three late arrivals in a month are counted as one half-day leave. Monthly attendance percentage is calculated as days present divided by total working days multiplied by 100, and at least 90% attendance is needed for bonus eligibility."]),
("12. Exit Process", [
 "To resign, an employee must submit a written resignation to the manager and HR and serve the notice period. An exit interview is held in the last week of employment.",
 "The final settlement is paid within 45 days after the last working day, once all company assets have been returned."]),
]

def build(path, title, sections):
    h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=16, spaceAfter=10)
    b = ParagraphStyle("b", fontName="Helvetica", fontSize=11, leading=16, spaceAfter=8)
    def footer(c, d):
        c.setFont("Helvetica", 8); c.drawString(20 * mm, 10 * mm, f"Nova Tech Solutions | {title} | Page {d.page}")
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=18*mm)
    story = []
    for i, (heading, paras) in enumerate(sections):
        story.append(Paragraph(heading, h))
        story.extend(Paragraph(p, b) for p in paras)
        if i < len(sections) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

def create(folder="documents"):
    os.makedirs(folder, exist_ok=True)
    build(os.path.join(folder, "Policy.pdf"), "Policy.pdf", POLICY)
    build(os.path.join(folder, "Handbook.pdf"), "Handbook.pdf", HANDBOOK)

if __name__ == "__main__":
    create()
    print("Created documents/Policy.pdf and documents/Handbook.pdf")
