"""
Email digest sender
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any
from datetime import datetime
from jinja2 import Template
from src.models.opportunity import Opportunity

class EmailSender:
    """Send weekly digest emails"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
    
    def generate_html_template(self, opportunities: List[Opportunity], insights: Dict[str, Any]) -> str:
        """Generate HTML email template"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Africa Digital Consultancy Radar - Weekly Digest</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 30px -30px;
                }
                .header h1 {
                    margin: 0;
                    font-size: 28px;
                }
                .header .date {
                    font-size: 16px;
                    opacity: 0.9;
                    margin-top: 10px;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .stat-card {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }
                .stat-card.high {
                    border-left-color: #e74c3c;
                }
                .stat-card .number {
                    font-size: 32px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .stat-card .label {
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 5px;
                }
                .opportunity {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    transition: all 0.3s ease;
                }
                .opportunity:hover {
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transform: translateY(-2px);
                }
                .opportunity.high {
                    border-left: 5px solid #e74c3c;
                }
                .opportunity.medium {
                    border-left: 5px solid #f39c12;
                }
                .opportunity.low {
                    border-left: 5px solid #27ae60;
                }
                .opportunity h3 {
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                }
                .opportunity .meta {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin: 15px 0;
                    font-size: 14px;
                }
                .opportunity .tag {
                    background: #e8f4fd;
                    color: #3498db;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }
                .opportunity .tag.skill {
                    background: #d5f4e6;
                    color: #27ae60;
                }
                .opportunity .tag.region {
                    background: #fdebd0;
                    color: #f39c12;
                }
                .opportunity .score {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 10px 0;
                }
                .opportunity .score.high {
                    color: #e74c3c;
                }
                .opportunity .score.medium {
                    color: #f39c12;
                }
                .opportunity .deadline {
                    background: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    font-size: 14px;
                }
                .insights {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 30px 0;
                }
                .insights h2 {
                    color: #2c3e50;
                    margin-top: 0;
                }
                .footer {
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    color: #7f8c8d;
                    font-size: 14px;
                }
                .button {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    margin: 10px 5px;
                }
                .button.secondary {
                    background: #6c757d;
                }
                .button-container {
                    text-align: center;
                    margin: 30px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 Africa Digital Consultancy Radar</h1>
                    <div class="date">Weekly Digest • {{ date }}</div>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="number">{{ total_opportunities }}</div>
                        <div class="label">Total Opportunities</div>
                    </div>
                    <div class="stat-card high">
                        <div class="number">{{ high_priority_count }}</div>
                        <div class="label">High Priority</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{{ medium_priority_count }}</div>
                        <div class="label">Medium Priority</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">{{ active_organizations_count }}</div>
                        <div class="label">Active Organizations</div>
                    </div>
                </div>
                
                {% if insights %}
                <div class="insights">
                    <h2>📊 Weekly Insights</h2>
                    
                    <h3>Most Requested Skills:</h3>
                    <div style="margin-bottom: 15px;">
                        {% for skill in insights.most_requested_skills %}
                        <span class="tag skill">{{ skill.skill }} ({{ skill.count }})</span>
                        {% endfor %}
                    </div>
                    
                    <h3>Active Regions:</h3>
                    <div style="margin-bottom: 15px;">
                        {% for region in insights.active_regions %}
                        <span class="tag region">{{ region.region }} ({{ region.count }})</span>
                        {% endfor %}
                    </div>
                    
                    <h3>Trends This Week:</h3>
                    <ul>
                        {% for trend in insights.trends %}
                        <li>{{ trend }}</li>
                        {% endfor %}
                    </ul>
                    
                    <h3>Recommendations:</h3>
                    <ul>
                        {% for recommendation in insights.recommendations %}
                        <li>{{ recommendation }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                <div class="button-container">
                    <a href="https://www.notion.so" class="button">View Full Database</a>
                    <a href="#" class="button secondary">Export to CSV</a>
                </div>
                
                <h2>🔥 High Priority Opportunities</h2>
                {% for opp in high_priority_opportunities %}
                <div class="opportunity high">
                    <h3>{{ opp.title }}</h3>
                    <div class="meta">
                        <span><strong>Organization:</strong> {{ opp.organization }}</span>
                        <span><strong>Contract:</strong> {{ opp.contract_type.value }}</span>
                        {% if opp.deadline %}
                        <span><strong>Deadline:</strong> {{ opp.deadline.strftime('%Y-%m-%d') }}</span>
                        {% endif %}
                    </div>
                    
                    <div class="meta">
                        {% for skill in opp.primary_skills[:3] %}
                        <span class="tag skill">{{ skill }}</span>
                        {% endfor %}
                        {% for region in opp.regions[:2] %}
                        <span class="tag region">{{ region.value }}</span>
                        {% endfor %}
                    </div>
                    
                    <div class="score high">Score: {{ opp.relevance_score }}/100</div>
                    
                    {% if opp.deadline and (opp.deadline - now).days < 7 %}
                    <div class="deadline">
                        ⚠️ Deadline approaching in {{ (opp.deadline - now).days }} days
                    </div>
                    {% endif %}
                    
                    <p>{{ opp.ai_summary }}</p>
                    
                    <div class="meta">
                        <a href="{{ opp.url }}" target="_blank">View Opportunity</a>
                        <span>Source: {{ opp.source_platform.value }}</span>
                    </div>
                </div>
                {% endfor %}
                
                {% if medium_priority_opportunities %}
                <h2>📈 Medium Priority Opportunities</h2>
                {% for opp in medium_priority_opportunities[:3] %}
                <div class="opportunity medium">
                    <h3>{{ opp.title }}</h3>
                    <div class="score medium">Score: {{ opp.relevance_score }}/100</div>
                    <a href="{{ opp.url }}" target="_blank">View Details</a>
                </div>
                {% endfor %}
                {% endif %}
                
                <div class="footer">
                    <p>This email was automatically generated by Africa Digital Consultancy Radar.</p>
                    <p>To unsubscribe or manage preferences, contact your system administrator.</p>
                    <p>© {{ year }} Africa Digital Consultancy Radar. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Prepare data for template
        high_priority = [opp for opp in opportunities if opp.priority.value == "High"]
        medium_priority = [opp for opp in opportunities if opp.priority.value == "Medium"]
        
        # Count unique organizations
        orgs = set(opp.organization for opp in opportunities)
        
        template = Template(html_template)
        html_content = template.render(
            date=datetime.now().strftime("%B %d, %Y"),
            total_opportunities=len(opportunities),
            high_priority_count=len(high_priority),
            medium_priority_count=len(medium_priority),
            active_organizations_count=len(orgs),
            insights=insights,
            high_priority_opportunities=high_priority,
            medium_priority_opportunities=medium_priority,
            now=datetime.now(),
            year=datetime.now().year
        )
        
        return html_content
    
    def send_digest(self, opportunities: List[Opportunity], insights: Dict[str, Any],
                    recipients: List[str], subject: str = None):
        """Send weekly digest email"""
        if not recipients:
            print("No recipients specified")
            return
        
        try:
            # Generate HTML content
            html_content = self.generate_html_template(opportunities, insights)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject or f"Africa Digital Consultancy Radar - Weekly Digest {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {len(recipients)} recipients")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")