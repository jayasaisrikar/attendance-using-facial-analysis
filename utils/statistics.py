import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.db.models import Count, Avg
from datetime import datetime, timedelta

class AttendanceAnalytics:
    def __init__(self, attendance_data):
        self.attendance_data = attendance_data

    def generate_monthly_report(self):
        """
        Generates monthly attendance statistics
        Returns DataFrame with monthly attendance percentages
        """
        df = pd.DataFrame(list(self.attendance_data.values(
            'date', 'is_present', 'subject'
        )))
        
        if df.empty:
            return pd.DataFrame(columns=['month', 'total_classes', 'attended', 'percentage'])
            
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
        
        monthly_stats = df.groupby('month').agg({
            'is_present': ['count', 'sum']
        }).reset_index()
        
        monthly_stats.columns = ['month', 'total_classes', 'attended']
        monthly_stats['percentage'] = (
            monthly_stats['attended'] / monthly_stats['total_classes'] * 100
        ).round(2)
        
        return monthly_stats

    def generate_subject_wise_report(self):
        """
        Generates subject-wise attendance statistics
        Returns DataFrame with subject-wise attendance percentages
        """
        df = pd.DataFrame(list(self.attendance_data.values(
            'subject', 'is_present'
        )))
        
        if df.empty:
            return pd.DataFrame(columns=['subject', 'total_classes', 'attended', 'percentage'])
            
        subject_stats = df.groupby('subject').agg({
            'is_present': ['count', 'sum']
        }).reset_index()
        
        subject_stats.columns = ['subject', 'total_classes', 'attended']
        subject_stats['percentage'] = (
            subject_stats['attended'] / subject_stats['total_classes'] * 100
        ).round(2)
        
        return subject_stats

    def generate_attendance_graph(self):
        """
        Generates a line graph of attendance trends
        Returns base64 encoded image
        """
        plt.switch_backend('Agg')  # Required for non-interactive environments
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get monthly statistics
        monthly_stats = self.generate_monthly_report()
        
        if not monthly_stats.empty:
            # Plot line graph
            sns.lineplot(data=monthly_stats, x='month', y='percentage', marker='o')
            
            # Customize the plot
            plt.title('Monthly Attendance Trend', pad=20)
            plt.xlabel('Month')
            plt.ylabel('Attendance Percentage')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Ensure percentage axis goes from 0 to 100
            plt.ylim(0, 100)
            
            # Add percentage labels on points
            for i, row in monthly_stats.iterrows():
                ax.annotate(f'{row["percentage"]}%', 
                          (i, row['percentage']),
                          textcoords="offset points", 
                          xytext=(0,10), 
                          ha='center')
        
        plt.tight_layout()
        
        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        return graphic

    def get_attendance_summary(self):
        """
        Generates a comprehensive attendance summary
        Returns dictionary with various attendance metrics
        """
        total_classes = self.attendance_data.count()
        total_present = self.attendance_data.filter(is_present=True).count()
        
        if total_classes > 0:
            overall_percentage = (total_present / total_classes) * 100
        else:
            overall_percentage = 0
            
        # Last 30 days statistics
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_attendance = self.attendance_data.filter(date__gte=thirty_days_ago)
        recent_total = recent_attendance.count()
        recent_present = recent_attendance.filter(is_present=True).count()
        
        if recent_total > 0:
            recent_percentage = (recent_present / recent_total) * 100
        else:
            recent_percentage = 0

        return {
            'total_classes': total_classes,
            'total_present': total_present,
            'overall_percentage': round(overall_percentage, 2),
            'recent_total': recent_total,
            'recent_present': recent_present,
            'recent_percentage': round(recent_percentage, 2)
        }

    def get_daily_attendance_pattern(self):
        """
        Analyzes daily attendance patterns
        Returns DataFrame with day-wise attendance statistics
        """
        df = pd.DataFrame(list(self.attendance_data.values('date', 'is_present')))
        
        if df.empty:
            return pd.DataFrame(columns=['day', 'total_classes', 'attended', 'percentage'])
            
        df['day'] = pd.to_datetime(df['date']).dt.day_name()
        
        daily_stats = df.groupby('day').agg({
            'is_present': ['count', 'sum']
        }).reset_index()
        
        daily_stats.columns = ['day', 'total_classes', 'attended']
        daily_stats['percentage'] = (
            daily_stats['attended'] / daily_stats['total_classes'] * 100
        ).round(2)
        
        # Sort by days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_stats['day'] = pd.Categorical(daily_stats['day'], categories=day_order, ordered=True)
        daily_stats = daily_stats.sort_values('day')
        
        return daily_stats

    def generate_heatmap(self):
        """
        Generates a heatmap of attendance patterns
        Returns base64 encoded image
        """
        plt.switch_backend('Agg')
        
        df = pd.DataFrame(list(self.attendance_data.values('date', 'is_present')))
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['day'] = df['date'].dt.day_name()
            df['week'] = df['date'].dt.isocalendar().week
            
            # Create pivot table for heatmap
            pivot_table = df.pivot_table(
                values='is_present',
                index='week',
                columns='day',
                aggfunc='mean'
            ) * 100
            
            # Create heatmap
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot_table, 
                       annot=True, 
                       fmt='.1f', 
                       cmap='YlOrRd',
                       cbar_kws={'label': 'Attendance %'})
            
            plt.title('Weekly Attendance Pattern')
            plt.xlabel('Day of Week')
            plt.ylabel('Week Number')
            
            # Convert plot to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            plt.close()
            
            return base64.b64encode(image_png).decode('utf-8')
        
        return None

    def export_to_excel(self):
        """
        Exports attendance data to Excel file
        Returns BytesIO object containing Excel file
        """
        output = BytesIO()
        
        # Create Excel writer object
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Monthly Report
            monthly_stats = self.generate_monthly_report()
            monthly_stats.to_excel(writer, sheet_name='Monthly Report', index=False)
            
            # Subject-wise Report
            subject_stats = self.generate_subject_wise_report()
            subject_stats.to_excel(writer, sheet_name='Subject Report', index=False)
            
            # Daily Pattern
            daily_stats = self.get_daily_attendance_pattern()
            daily_stats.to_excel(writer, sheet_name='Daily Pattern', index=False)
            
            # Raw Data
            df = pd.DataFrame(list(self.attendance_data.values()))
            df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            
            # Add some formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            # Format all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                worksheet.set_row(0, None, header_format)
                worksheet.set_column('A:Z', 15)  # Set column width
        
        output.seek(0)
        return output