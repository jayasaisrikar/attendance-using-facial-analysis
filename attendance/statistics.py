import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

class AttendanceAnalytics:
    def __init__(self, attendance_data):
        self.attendance_data = attendance_data
        
    def generate_monthly_report(self):
        df = pd.DataFrame(self.attendance_data.values())
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
        monthly_stats = df.groupby('month').agg({
            'is_present': ['count', 'sum']
        }).reset_index()
        
        monthly_stats['percentage'] = (
            monthly_stats[('is_present', 'sum')] / 
            monthly_stats[('is_present', 'count')] * 100
        )
        
        return monthly_stats
        
    def generate_subject_wise_report(self):
        df = pd.DataFrame(self.attendance_data.values())
        subject_stats = df.groupby('subject').agg({
            'is_present': ['count', 'sum']
        }).reset_index()
        
        subject_stats['percentage'] = (
            subject_stats[('is_present', 'sum')] / 
            subject_stats[('is_present', 'count')] * 100
        )
        
        return subject_stats
        
    def generate_attendance_graph(self):
        plt.figure(figsize=(10, 6))
        df = pd.DataFrame(self.attendance_data.values())
        df['date'] = pd.to_datetime(df['date'])
        
        monthly_attendance = df.groupby(df['date'].dt.strftime('%B %Y'))['is_present'].mean() * 100
        
        plt.plot(monthly_attendance.index, monthly_attendance.values, marker='o')
        plt.title('Monthly Attendance Trend')
        plt.xlabel('Month')
        plt.ylabel('Attendance Percentage')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        return graphic