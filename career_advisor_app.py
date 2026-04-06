# career_advisor_app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import io
import os
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile

# Page config
st.set_page_config(
    page_title="AI Career Path Advisor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .report-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .fit-score {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .skill-badge {
        background: #f0f0f0;
        padding: 0.25rem 0.75rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        display: inline-block;
        margin: 0.25rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 2rem;
        font-weight: bold;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Career Paths Database
CAREER_PATHS = {
    "Software Developer": {
        "skills_required": {"Technical/Coding": 4, "Data Analysis": 3, "Communication & Writing": 3, "Leadership & Management": 2, "Creative & Design": 2},
        "interests": ["Technology", "Building things"],
        "salary_range": "$70,000 - $120,000",
        "growth_outlook": "Excellent (22% growth projected)",
        "description": "Design, code, and maintain software applications and systems. Software developers create the applications that power our digital world.",
        "milestones": {
            "6_months": "Complete a coding bootcamp or certification",
            "1_year": "Build 2-3 portfolio projects and contribute to open source",
            "3_years": "Master a framework and lead small projects"
        },
        "required_skills_list": ["Python/Java/JavaScript", "Problem Solving", "Version Control (Git)", "Database Management", "API Development"]
    },
    "Data Scientist": {
        "skills_required": {"Technical/Coding": 4, "Data Analysis": 5, "Communication & Writing": 3, "Leadership & Management": 2, "Creative & Design": 2},
        "interests": ["Technology", "Analyzing data"],
        "salary_range": "$80,000 - $130,000",
        "growth_outlook": "Excellent (35% growth projected)",
        "description": "Analyze complex data to help organizations make better decisions. Data scientists combine statistics, programming, and business acumen.",
        "milestones": {
            "6_months": "Learn Python and SQL fundamentals",
            "1_year": "Complete data science certification and build portfolio",
            "3_years": "Master machine learning and lead data projects"
        },
        "required_skills_list": ["Python/R", "Statistics", "Machine Learning", "SQL", "Data Visualization"]
    },
    "Product Manager": {
        "skills_required": {"Technical/Coding": 2, "Data Analysis": 3, "Communication & Writing": 4, "Leadership & Management": 4, "Creative & Design": 3},
        "interests": ["Technology", "People", "Leading"],
        "salary_range": "$90,000 - $140,000",
        "growth_outlook": "Strong (15% growth projected)",
        "description": "Guide product development from concept to launch. Product managers bridge business, technology, and user experience.",
        "milestones": {
            "6_months": "Learn agile methodologies and product management tools",
            "1_year": "Lead a small product feature from ideation to launch",
            "3_years": "Manage full product lifecycle and stakeholder relationships"
        },
        "required_skills_list": ["Agile/Scrum", "User Research", "Strategic Thinking", "Communication", "Data Analysis"]
    },
    "UX/UI Designer": {
        "skills_required": {"Technical/Coding": 2, "Data Analysis": 2, "Communication & Writing": 3, "Leadership & Management": 2, "Creative & Design": 5},
        "interests": ["Creativity", "Building things", "People"],
        "salary_range": "$65,000 - $110,000",
        "growth_outlook": "Strong (13% growth projected)",
        "description": "Create intuitive and beautiful digital experiences. UX/UI designers focus on user-centered design and visual aesthetics.",
        "milestones": {
            "6_months": "Master design tools like Figma and build portfolio",
            "1_year": "Complete UX certification and real client projects",
            "3_years": "Lead design systems and mentor junior designers"
        },
        "required_skills_list": ["Figma/Sketch", "User Research", "Wireframing", "Prototyping", "Visual Design"]
    },
    "Marketing Manager": {
        "skills_required": {"Technical/Coding": 1, "Data Analysis": 3, "Communication & Writing": 5, "Leadership & Management": 3, "Creative & Design": 3},
        "interests": ["Creativity", "People", "Finance"],
        "salary_range": "$65,000 - $100,000",
        "growth_outlook": "Steady (10% growth projected)",
        "description": "Develop and execute marketing strategies. Marketing managers drive brand awareness and customer acquisition.",
        "milestones": {
            "6_months": "Learn digital marketing fundamentals and analytics",
            "1_year": "Manage a full marketing campaign",
            "3_years": "Lead marketing team and strategy development"
        },
        "required_skills_list": ["Digital Marketing", "Content Strategy", "SEO/SEM", "Analytics", "Campaign Management"]
    },
    "Project Manager": {
        "skills_required": {"Technical/Coding": 1, "Data Analysis": 3, "Communication & Writing": 4, "Leadership & Management": 4, "Creative & Design": 2},
        "interests": ["People", "Leading", "Building things"],
        "salary_range": "$70,000 - $110,000",
        "growth_outlook": "Strong (11% growth projected)",
        "description": "Plan, execute, and close projects across various industries. Project managers ensure timely delivery within budget.",
        "milestones": {
            "6_months": "Get PMP certification and learn project tools",
            "1_year": "Lead 2-3 medium-sized projects",
            "3_years": "Manage complex, cross-functional projects"
        },
        "required_skills_list": ["PMP/Agile", "Risk Management", "Budgeting", "Stakeholder Management", "Communication"]
    },
    "Business Analyst": {
        "skills_required": {"Technical/Coding": 2, "Data Analysis": 4, "Communication & Writing": 4, "Leadership & Management": 3, "Creative & Design": 2},
        "interests": ["Analyzing data", "Finance", "People"],
        "salary_range": "$65,000 - $95,000",
        "growth_outlook": "Steady (14% growth projected)",
        "description": "Bridge business needs with technical solutions. Business analysts translate requirements into actionable plans.",
        "milestones": {
            "6_months": "Learn SQL and business analysis tools",
            "1_year": "Lead requirement gathering for 3+ projects",
            "3_years": "Specialize in domain expertise and stakeholder management"
        },
        "required_skills_list": ["SQL", "Requirement Gathering", "Process Modeling", "Data Analysis", "Documentation"]
    },
    "Technical Writer": {
        "skills_required": {"Technical/Coding": 2, "Data Analysis": 1, "Communication & Writing": 5, "Leadership & Management": 2, "Creative & Design": 2},
        "interests": ["Technology", "People", "Creativity"],
        "salary_range": "$55,000 - $85,000",
        "growth_outlook": "Steady (7% growth projected)",
        "description": "Create clear documentation for technical products. Technical writers make complex information accessible.",
        "milestones": {
            "6_months": "Build technical writing portfolio",
            "1_year": "Document 5+ technical projects",
            "3_years": "Lead documentation strategy for products"
        },
        "required_skills_list": ["Technical Writing", "Documentation Tools", "Research", "Editing", "API Documentation"]
    },
    "Sales Executive": {
        "skills_required": {"Technical/Coding": 1, "Data Analysis": 2, "Communication & Writing": 5, "Leadership & Management": 3, "Creative & Design": 2},
        "interests": ["People", "Finance", "Leading"],
        "salary_range": "$50,000 - $150,000 (with commission)",
        "growth_outlook": "Steady (5% growth projected)",
        "description": "Drive revenue through relationship building and sales strategies. Sales executives are key drivers of business growth.",
        "milestones": {
            "6_months": "Learn sales methodologies and CRM tools",
            "1_year": "Achieve 100% of quota consistently",
            "3_years": "Manage key accounts and lead sales teams"
        },
        "required_skills_list": ["CRM Software", "Negotiation", "Relationship Building", "Communication", "Pipeline Management"]
    }
}

# Skill mapping for career matching
SKILL_WEIGHTS = {
    "Technical/Coding": 0.25,
    "Communication & Writing": 0.20,
    "Data Analysis": 0.20,
    "Leadership & Management": 0.20,
    "Creative & Design": 0.15
}

def calculate_fit_score(user_skills, career_requirements):
    """Calculate fit score between user skills and career requirements."""
    scores = []
    for skill, user_level in user_skills.items():
        if skill in career_requirements:
            required_level = career_requirements[skill]
            # Calculate score with diminishing returns for over-qualification
            if user_level >= required_level:
                score = 1.0
            else:
                score = user_level / required_level
            scores.append(score * SKILL_WEIGHTS.get(skill, 0.2))
    return sum(scores) * 100

def match_interests(user_interests, career_interests):
    """Calculate interest match percentage."""
    if not user_interests or not career_interests:
        return 50
    common = len(set(user_interests) & set(career_interests))
    total = len(set(user_interests) | set(career_interests))
    return (common / total * 100) if total > 0 else 0

def get_career_recommendations(user_data):
    """Generate career recommendations based on user input."""
    recommendations = []
    
    # Parse user skills
    user_skills = {
        "Technical/Coding": user_data.get("technical_rating", 2),
        "Communication & Writing": user_data.get("communication_rating", 2),
        "Data Analysis": user_data.get("data_rating", 2),
        "Leadership & Management": user_data.get("leadership_rating", 2),
        "Creative & Design": user_data.get("creative_rating", 2)
    }
    
    # Parse interests
    user_interests = user_data.get("interests", [])
    if isinstance(user_interests, str):
        user_interests = [i.strip() for i in user_interests.split(",")]
    
    # Calculate scores for each career
    for career_name, career_data in CAREER_PATHS.items():
        skill_score = calculate_fit_score(user_skills, career_data["skills_required"])
        interest_score = match_interests(user_interests, career_data["interests"])
        
        # Combined score (70% skill, 30% interest)
        total_score = (skill_score * 0.7) + (interest_score * 0.3)
        
        # Add career stage adjustment
        career_stage = user_data.get("career_stage", "Student")
        if career_stage == "Student" and total_score < 50:
            # Students get slightly higher recommendations to encourage exploration
            total_score = min(100, total_score * 1.1)
        
        recommendations.append({
            "career": career_name,
            "fit_score": round(total_score, 1),
            "skill_score": round(skill_score, 1),
            "interest_score": round(interest_score, 1),
            "description": career_data["description"],
            "skills_required": career_data["skills_required"],
            "required_skills_list": career_data.get("required_skills_list", []),
            "salary_range": career_data["salary_range"],
            "growth_outlook": career_data["growth_outlook"],
            "milestones": career_data["milestones"]
        })
    
    # Sort by fit score
    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    return recommendations[:5]  # Return top 5

def create_skills_radar_chart(user_skills):
    """Create radar chart for skills visualization."""
    categories = list(user_skills.keys())
    values = list(user_skills.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#667eea',
        fillcolor='rgba(102, 126, 234, 0.2)',
        marker=dict(color='#667eea', size=6)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['1', '2', '3', '4', '5']
            ),
            angularaxis=dict(
                tickfont=dict(size=10)
            )
        ),
        showlegend=False,
        title="Your Skills Profile",
        height=450,
        margin=dict(l=80, r=80, t=50, b=50)
    )
    
    return fig

def create_pdf_report(user_data, recommendations):
    """Generate PDF report using reportlab."""
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading1']
    heading2_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    center_style = ParagraphStyle(
        'CenterStyle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12
    )
    
    # Title
    story.append(Paragraph("AI Career Path Advisor Report", title_style))
    story.append(Spacer(1, 12))
    
    # Date
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", center_style))
    story.append(Spacer(1, 20))
    
    # User Summary
    story.append(Paragraph("User Profile Summary", heading_style))
    story.append(Spacer(1, 12))
    
    user_summary = [
        f"<b>Career Stage:</b> {user_data.get('career_stage', 'Not specified')}",
        f"<b>Primary Goal:</b> {user_data.get('primary_goal', 'Not specified')}",
        f"<b>Industries:</b> {', '.join(user_data.get('industries', [])) if user_data.get('industries') else 'Not specified'}",
        f"<b>Hard Skills:</b> {user_data.get('hard_skills', 'Not specified')}"
    ]
    
    for line in user_summary:
        story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))
    
    # Top Recommendations
    story.append(Paragraph("Top Career Recommendations", heading_style))
    story.append(Spacer(1, 12))
    
    for i, rec in enumerate(recommendations[:3], 1):
        story.append(Paragraph(f"{i}. {rec['career']} - Fit Score: {rec['fit_score']}%", heading2_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(rec['description'], normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Salary Range:</b> {rec['salary_range']}", normal_style))
        story.append(Paragraph(f"<b>Growth Outlook:</b> {rec['growth_outlook']}", normal_style))
        story.append(Spacer(1, 12))
        
        # Required skills
        story.append(Paragraph("<b>Key Skills Required:</b>", normal_style))
        for skill in rec['required_skills_list'][:5]:
            story.append(Paragraph(f"• {skill}", normal_style))
        story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Action Plan
    story.append(Paragraph("Your 30/60/90 Day Action Plan", heading_style))
    story.append(Spacer(1, 12))
    
    for rec in recommendations[:2]:
        story.append(Paragraph(f"For {rec['career']}:", heading2_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>First 30 Days:</b> {rec['milestones']['6_months'].split('and')[0].strip()}", normal_style))
        story.append(Spacer(1, 6))
        
        if 'and' in rec['milestones']['6_months']:
            story.append(Paragraph(f"<b>Next 60 Days:</b> {rec['milestones']['6_months'].split('and')[-1].strip()}", normal_style))
        else:
            story.append(Paragraph(f"<b>Next 60 Days:</b> Continue building foundational skills", normal_style))
        
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>90 Days:</b> {rec['milestones']['1_year'].split('and')[0].strip()}", normal_style))
        story.append(Spacer(1, 12))
    
    story.append(Spacer(1, 20))
    
    # Skills Gap Analysis
    story.append(Paragraph("Skills Gap Analysis", heading_style))
    story.append(Spacer(1, 12))
    
    user_skills = {
        "Technical/Coding": user_data.get("technical_rating", 2),
        "Communication & Writing": user_data.get("communication_rating", 2),
        "Data Analysis": user_data.get("data_rating", 2),
        "Leadership & Management": user_data.get("leadership_rating", 2),
        "Creative & Design": user_data.get("creative_rating", 2)
    }
    
    for skill, level in user_skills.items():
        story.append(Paragraph(f"<b>{skill}:</b> Level {level}/5", normal_style))
        story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 20))
    
    # Next Steps
    story.append(Paragraph("Recommended Next Steps", heading_style))
    story.append(Spacer(1, 12))
    
    next_steps = [
        "1. Review the recommended career paths and research which aligns best with your interests",
        "2. Identify skill gaps and create a learning plan",
        "3. Connect with professionals in your target roles on LinkedIn",
        "4. Update your resume to highlight relevant skills",
        "5. Consider taking online courses to build required competencies"
    ]
    
    for step in next_steps:
        story.append(Paragraph(step, normal_style))
        story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    return temp_file.name

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Career Path Advisor</h1>
        <p>Discover your ideal career path through intelligent, personalized AI guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = None
    
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    
    # Input method selection
    input_method = st.radio(
        "How would you like to get your career advice?",
        ["📝 Fill out the questionnaire", "📊 View sample report (demo)"],
        horizontal=True
    )
    
    if input_method == "📝 Fill out the questionnaire":
        st.markdown("### 📋 Career Assessment Questionnaire")
        st.markdown("Complete this short questionnaire to get personalized career recommendations.")
        
        # Create two columns for the form
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Section A: Personal Interests")
            interests = st.multiselect(
                "What topics or subjects energize you the most?",
                ["Technology", "People", "Finance", "Creativity", "Nature", "Science", "Arts", "Business"]
            )
            
            work_preferences = st.multiselect(
                "How do you prefer to spend your work time?",
                ["Building things", "Helping others", "Analyzing data", "Leading", "Creating content", "Problem solving"]
            )
            
            work_env = st.selectbox(
                "Which work environment appeals to you?",
                ["Remote", "Hybrid", "On-site", "Flexible"]
            )
        
        with col2:
            st.markdown("#### Section B: Skills Assessment")
            technical_rating = st.slider("Technical/Coding", 1, 5, 3, help="Rate your comfort with programming and technical concepts")
            comm_rating = st.slider("Communication & Writing", 1, 5, 3, help="Rate your written and verbal communication skills")
            data_rating = st.slider("Data Analysis", 1, 5, 3, help="Rate your ability to analyze and interpret data")
            leadership_rating = st.slider("Leadership & Management", 1, 5, 3, help="Rate your leadership and people management skills")
            creative_rating = st.slider("Creative & Design", 1, 5, 3, help="Rate your creative thinking and design abilities")
            
            hard_skills = st.text_input("List your top 3 hard skills (certifications, tools, technologies)", 
                                       placeholder="e.g., Python, Project Management, Data Analysis")
        
        # Section C
        st.markdown("#### Section C: Goals & Context")
        col3, col4 = st.columns(2)
        
        with col3:
            career_stage = st.selectbox(
                "What is your current career stage?",
                ["Student", "Early career (0-2 years)", "Mid-career (3-7 years)", "Career Changer", "Senior (8+ years)"]
            )
            
            primary_goal = st.selectbox(
                "What is your primary career goal in the next 12 months?",
                ["Get first job", "Get promoted", "Switch industries", "Start business", "Explore options"]
            )
        
        with col4:
            industries = st.multiselect(
                "What industries are you open to?",
                ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Non-profit"]
            )
            
            constraints = st.text_area("Any constraints we should know about? (location, salary, etc.)", 
                                      placeholder="Optional - e.g., Remote only, Minimum salary $60k, etc.")
        
        # Submit button
        if st.button("🔮 Generate My Career Report", use_container_width=True):
            # Prepare user data
            user_data = {
                "interests": interests,
                "work_preferences": work_preferences,
                "work_environment": work_env,
                "technical_rating": technical_rating,
                "communication_rating": comm_rating,
                "data_rating": data_rating,
                "leadership_rating": leadership_rating,
                "creative_rating": creative_rating,
                "hard_skills": hard_skills if hard_skills else "Not specified",
                "career_stage": career_stage,
                "primary_goal": primary_goal,
                "industries": industries,
                "constraints": constraints if constraints else "None specified"
            }
            
            st.session_state.form_data = user_data
            st.session_state.report_generated = True
            st.rerun()
    
    elif input_method == "📊 View sample report (demo)":
        # Demo data
        demo_data = {
            "interests": ["Technology", "Creativity", "People"],
            "work_preferences": ["Building things", "Analyzing data"],
            "work_environment": "Hybrid",
            "technical_rating": 4,
            "communication_rating": 4,
            "data_rating": 3,
            "leadership_rating": 3,
            "creative_rating": 4,
            "hard_skills": "Python, Figma, SQL",
            "career_stage": "Early career (0-2 years)",
            "primary_goal": "Get promoted",
            "industries": ["Technology", "Finance"],
            "constraints": "Remote preferred"
        }
        st.session_state.form_data = demo_data
        st.session_state.report_generated = True
        st.rerun()
    
    # Display report if generated
    if st.session_state.report_generated and st.session_state.form_data:
        st.markdown("---")
        st.markdown("## 📊 Your Personalized Career Report")
        
        user_data = st.session_state.form_data
        
        # Get recommendations
        recommendations = get_career_recommendations(user_data)
        
        # Top Recommendations Section
        st.markdown("### 🎯 Top Career Recommendations")
        
        cols = st.columns(3)
        for idx, rec in enumerate(recommendations[:3]):
            with cols[idx]:
                st.markdown(f"""
                <div class="report-card">
                    <h3>{rec['career']}</h3>
                    <div class="fit-score">{rec['fit_score']}%</div>
                    <p>Fit Score</p>
                    <hr>
                    <p><strong>Salary Range:</strong><br>{rec['salary_range']}</p>
                    <p><strong>Growth:</strong> {rec['growth_outlook']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Skills Snapshot
        st.markdown("### 📈 Skills Snapshot")
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            user_skills = {
                "Technical/Coding": user_data.get("technical_rating", 3),
                "Communication": user_data.get("communication_rating", 3),
                "Data Analysis": user_data.get("data_rating", 3),
                "Leadership": user_data.get("leadership_rating", 3),
                "Creative": user_data.get("creative_rating", 3)
            }
            
            # Display skill badges
            st.markdown("**Your Skill Levels:**")
            for skill, level in user_skills.items():
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <span class="skill-badge">{skill}</span>
                    <div style="background: #e0e0e0; border-radius: 10px; height: 8px; margin-top: 5px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); width: {level*20}%; height: 8px; border-radius: 10px;"></div>
                    </div>
                    <span style="font-size: 0.8rem;">Level {level}/5</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Radar chart
            fig = create_skills_radar_chart(user_skills)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Career Analysis
        st.markdown("### 🔍 Detailed Career Analysis")
        
        for rec in recommendations[:2]:
            with st.expander(f"📌 {rec['career']} - {rec['fit_score']}% Match", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Role Overview:**\n{rec['description']}")
                    st.markdown(f"**Salary Range:** {rec['salary_range']}")
                    st.markdown(f"**Growth Outlook:** {rec['growth_outlook']}")
                    
                    st.markdown("**Key Skills Required:**")
                    for skill in rec['required_skills_list'][:5]:
                        st.markdown(f"- {skill}")
                
                with col2:
                    st.markdown("**Skills Required (Levels):**")
                    for skill, level in rec['skills_required'].items():
                        st.markdown(f"- {skill}: Level {level}/5")
                
                st.markdown("---")
                st.markdown("#### 🗺️ Your Action Plan")
                
                # Create tabs for timeline
                tab1, tab2, tab3 = st.tabs(["📅 30 Days", "📅 60 Days", "📅 90 Days"])
                
                with tab1:
                    st.markdown(f"✅ {rec['milestones']['6_months'].split('and')[0].strip()}")
                    st.info("💡 Focus on building foundational knowledge and skills")
                
                with tab2:
                    if 'and' in rec['milestones']['6_months']:
                        st.markdown(f"✅ {rec['milestones']['6_months'].split('and')[-1].strip()}")
                    else:
                        st.markdown(f"✅ Continue building foundational skills and start networking")
                    st.info("💡 Start connecting with professionals in this field")
                
                with tab3:
                    st.markdown(f"✅ {rec['milestones']['1_year'].split('and')[0].strip()}")
                    st.info("💡 Begin applying for entry-level positions or internships")
        
        # Recruiter-Ready Summary
        st.markdown("### 📄 Recruiter-Ready Summary")
        
        recruiter_summary = f"""
        <div class="report-card" style="background: #f8f9fa;">
            <h4>Professional Summary</h4>
            <p><strong>🎓 Career Stage:</strong> {user_data.get('career_stage', 'Not specified')}</p>
            <p><strong>🎯 Primary Goal:</strong> {user_data.get('primary_goal', 'Not specified')}</p>
            <p><strong>⚡ Top Skills:</strong> {user_data.get('hard_skills', 'Not specified')}</p>
            <p><strong>💼 Recommended Roles:</strong> {', '.join([rec['career'] for rec in recommendations[:3]])}</p>
            <p><strong>🏢 Industries of Interest:</strong> {', '.join(user_data.get('industries', [])) if user_data.get('industries') else 'Open to various'}</p>
            <hr>
            <p><em>✨ This candidate demonstrates strong alignment with {recommendations[0]['career'] if recommendations else 'recommended'} roles, 
            with a {recommendations[0]['fit_score']}% fit score based on skills and interests assessment. 
            They show particular strength in {list(user_skills.keys())[list(user_skills.values()).index(max(user_skills.values()))]} 
            and are actively pursuing career development opportunities.</em></p>
        </div>
        """
        st.markdown(recruiter_summary, unsafe_allow_html=True)
        
        # PDF Download
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Download Full Report (PDF)", use_container_width=True):
                with st.spinner("📄 Generating your PDF report..."):
                    try:
                        pdf_path = create_pdf_report(user_data, recommendations)
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.download_button(
                            label="💾 Click here to download PDF",
                            data=pdf_bytes,
                            file_name=f"career_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Clean up temp file
                        try:
                            os.unlink(pdf_path)
                        except:
                            pass
                        
                        st.markdown('<div class="success-message">✅ PDF report generated successfully! Click the button above to download.</div>', 
                                  unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                        st.info("You can still view the report above. Try refreshing the page if you need to download.")
        
        # Share option
        st.info("💡 **Tip:** Copy the recruiter-ready summary above to share with potential employers or mentors!")
        
        # Re-assessment option
        st.markdown("---")
        if st.button("🔄 Take Assessment Again", use_container_width=True):
            st.session_state.report_generated = False
            st.session_state.form_data = None
            st.rerun()

# Add PageBreak function for PDF
def PageBreak():
    from reportlab.platypus import PageBreak
    return PageBreak()

if __name__ == "__main__":
    main()
