"""
Performance Tracker
Logs investment decisions and tracks performance over time
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import csv


class PerformanceTracker:
    """
    Tracks investment decisions and enables performance review
    
    Features:
    - Logs each analysis with date, ticker, model, decision
    - Records price at analysis time vs current price
    - Calculates actual returns vs expected returns
    - Generates performance reports
    """
    
    def __init__(self, log_dir: str = "performance_logs"):
        """
        Initialize performance tracker
        
        Args:
            log_dir: Directory to store performance logs
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Main log files
        self.json_log = os.path.join(log_dir, "decisions_log.json")
        self.csv_log = os.path.join(log_dir, "decisions_log.csv")
        
        # Initialize log files if they don't exist
        self._initialize_logs()
    
    def _initialize_logs(self):
        """Create log files if they don't exist"""
        # JSON log
        if not os.path.exists(self.json_log):
            with open(self.json_log, 'w') as f:
                json.dump([], f)
        
        # CSV log with headers
        if not os.path.exists(self.csv_log):
            headers = [
                'timestamp', 'date', 'ticker', 'company_name', 'sector',
                'model', 'recommendation', 'conviction', 'position_size',
                'current_price', 'fair_value', 'upside_percent',
                'intrinsic_value_range', 'margin_of_safety',
                'quality_score', 'moat_rating', 'risk_score', 'risk_rating',
                'expected_return_3y', 'composite_score',
                'value_rec', 'growth_rec', 'risk_rec',
                'analyst_agreement', 'key_catalyst', 'stop_loss',
                'output_file', 'notes'
            ]
            with open(self.csv_log, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
    
    def log_decision(self, analysis_data: Dict) -> None:
        """
        Log an investment decision
        
        Args:
            analysis_data: Dictionary containing analysis results
                Required keys:
                - ticker: Stock ticker
                - current_price: Price at analysis time
                - recommendation: BUY/SELL/HOLD
                - model: Model used (e.g., gemini-3-flash-preview)
                
                Optional keys:
                - company_name, sector, conviction, position_size,
                  fair_value, upside_percent, intrinsic_value_range,
                  margin_of_safety, quality_score, moat_rating,
                  risk_score, risk_rating, expected_return_3y,
                  composite_score, value_rec, growth_rec, risk_rec,
                  analyst_agreement, key_catalyst, stop_loss,
                  output_file, notes
        """
        # Create log entry
        timestamp = datetime.now().isoformat()
        date = datetime.now().strftime('%Y-%m-%d')
        
        log_entry = {
            'timestamp': timestamp,
            'date': date,
            'ticker': analysis_data.get('ticker', 'UNKNOWN'),
            'company_name': analysis_data.get('company_name', ''),
            'sector': analysis_data.get('sector', ''),
            'model': analysis_data.get('model', 'unknown'),
            'recommendation': analysis_data.get('recommendation', 'UNKNOWN'),
            'conviction': analysis_data.get('conviction', None),
            'position_size': analysis_data.get('position_size', None),
            'current_price': analysis_data.get('current_price', None),
            'fair_value': analysis_data.get('fair_value', None),
            'upside_percent': analysis_data.get('upside_percent', None),
            'intrinsic_value_range': analysis_data.get('intrinsic_value_range', ''),
            'margin_of_safety': analysis_data.get('margin_of_safety', None),
            'quality_score': analysis_data.get('quality_score', None),
            'moat_rating': analysis_data.get('moat_rating', ''),
            'risk_score': analysis_data.get('risk_score', None),
            'risk_rating': analysis_data.get('risk_rating', ''),
            'expected_return_3y': analysis_data.get('expected_return_3y', None),
            'composite_score': analysis_data.get('composite_score', None),
            'value_rec': analysis_data.get('value_rec', ''),
            'growth_rec': analysis_data.get('growth_rec', ''),
            'risk_rec': analysis_data.get('risk_rec', ''),
            'analyst_agreement': analysis_data.get('analyst_agreement', ''),
            'key_catalyst': analysis_data.get('key_catalyst', ''),
            'stop_loss': analysis_data.get('stop_loss', None),
            'output_file': analysis_data.get('output_file', ''),
            'notes': analysis_data.get('notes', ''),
        }
        
        # Append to JSON log
        self._append_to_json(log_entry)
        
        # Append to CSV log
        self._append_to_csv(log_entry)
        
        print(f"📊 Decision logged: {log_entry['ticker']} - {log_entry['recommendation']}")
        print(f"   Log files: {self.json_log}, {self.csv_log}")
    
    def _append_to_json(self, log_entry: Dict) -> None:
        """Append entry to JSON log"""
        # Read existing data
        with open(self.json_log, 'r') as f:
            data = json.load(f)
        
        # Append new entry
        data.append(log_entry)
        
        # Write back
        with open(self.json_log, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _append_to_csv(self, log_entry: Dict) -> None:
        """Append entry to CSV log"""
        with open(self.csv_log, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            writer.writerow(log_entry)
    
    def get_all_decisions(self) -> List[Dict]:
        """
        Get all logged decisions
        
        Returns:
            List of decision dictionaries
        """
        with open(self.json_log, 'r') as f:
            return json.load(f)
    
    def get_decisions_by_ticker(self, ticker: str) -> List[Dict]:
        """
        Get all decisions for a specific ticker
        
        Args:
            ticker: Stock ticker
        
        Returns:
            List of decisions for that ticker
        """
        all_decisions = self.get_all_decisions()
        return [d for d in all_decisions if d['ticker'] == ticker]
    
    def get_decisions_by_recommendation(self, recommendation: str) -> List[Dict]:
        """
        Get all decisions with a specific recommendation
        
        Args:
            recommendation: BUY, SELL, HOLD, etc.
        
        Returns:
            List of matching decisions
        """
        all_decisions = self.get_all_decisions()
        return [d for d in all_decisions if d['recommendation'] == recommendation]
    
    def get_decisions_by_model(self, model: str) -> List[Dict]:
        """
        Get all decisions made with a specific model
        
        Args:
            model: Model name (e.g., gemini-3-flash-preview)
        
        Returns:
            List of decisions from that model
        """
        all_decisions = self.get_all_decisions()
        return [d for d in all_decisions if d['model'] == model]
    
    def get_recent_decisions(self, days: int = 30) -> List[Dict]:
        """
        Get decisions from the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of recent decisions
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        all_decisions = self.get_all_decisions()
        return [
            d for d in all_decisions 
            if datetime.fromisoformat(d['timestamp']) >= cutoff
        ]
    
    def generate_summary_report(self) -> str:
        """
        Generate a summary report of all decisions
        
        Returns:
            Formatted report string
        """
        decisions = self.get_all_decisions()
        
        if not decisions:
            return "No decisions logged yet."
        
        # Basic stats
        total = len(decisions)
        buy_count = len([d for d in decisions if d['recommendation'] == 'BUY'])
        sell_count = len([d for d in decisions if d['recommendation'] == 'SELL'])
        hold_count = len([d for d in decisions if d['recommendation'] == 'HOLD'])
        
        # Average conviction
        convictions = [d['conviction'] for d in decisions if d['conviction'] is not None]
        avg_conviction = sum(convictions) / len(convictions) if convictions else 0
        
        # Unique tickers
        tickers = set(d['ticker'] for d in decisions)
        
        # Models used
        models = set(d['model'] for d in decisions)
        
        report = f"""
================================================================================
INVESTMENT DECISION SUMMARY REPORT
================================================================================

Total Decisions: {total}
Date Range: {decisions[0]['date']} to {decisions[-1]['date']}

RECOMMENDATIONS:
- BUY:  {buy_count} ({buy_count/total*100:.1f}%)
- SELL: {sell_count} ({sell_count/total*100:.1f}%)
- HOLD: {hold_count} ({hold_count/total*100:.1f}%)

AVERAGE CONVICTION: {avg_conviction:.1f}/10

UNIQUE TICKERS ANALYZED: {len(tickers)}
{', '.join(sorted(tickers))}

MODELS USED: {len(models)}
{', '.join(sorted(models))}

================================================================================
RECENT DECISIONS (Last 10):
================================================================================
"""
        
        # Show last 10 decisions
        for decision in decisions[-10:]:
            report += f"""
{decision['date']} | {decision['ticker']:6s} | {decision['recommendation']:10s} | 
  Price: ${decision['current_price']:.2f} | Fair Value: ${decision['fair_value']:.2f} | 
  Conviction: {decision['conviction']}/10 | Model: {decision['model']}
"""
        
        return report
    
    def export_for_analysis(self, output_file: str = None) -> str:
        """
        Export decisions to a file for further analysis
        
        Args:
            output_file: Output file path (defaults to performance_logs/export_TIMESTAMP.json)
        
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.log_dir, f"export_{timestamp}.json")
        
        decisions = self.get_all_decisions()
        
        with open(output_file, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        print(f"📄 Exported {len(decisions)} decisions to: {output_file}")
        return output_file


def extract_decision_data(analyzer) -> Dict:
    """
    Extract decision data from InvestmentAnalyzer for logging
    
    Args:
        analyzer: InvestmentAnalyzer instance after analysis
    
    Returns:
        Dictionary with extracted data
    """
    # Get basic info from results
    company_info = analyzer.results.get('company_info', {})
    data = {
        'ticker': analyzer.ticker,
        'company_name': company_info.get('name', ''),
        'sector': company_info.get('sector', ''),
        'current_price': company_info.get('current_price', None),
    }
    
    # Extract from CIO synthesis
    cio_synthesis = analyzer.results.get('cio_synthesis', {})
    cio_decision = cio_synthesis.get('decision', '')
    cio_full = cio_synthesis.get('full_synthesis', '')
    
    # Try to extract from decision summary first, then full synthesis
    cio_text = cio_decision if cio_decision else cio_full
    
    if cio_text:
        # Parse recommendation
        if 'FINAL RECOMMENDATION' in cio_text or 'Recommendation:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Recommendation:' in line:
                    data['recommendation'] = line.split(':')[1].strip()
                    break
                elif 'RECOMMENDATION:' in line:
                    data['recommendation'] = line.split(':')[1].strip().split()[0]
                    break
        
        # Parse conviction
        if 'Conviction:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Conviction:' in line:
                    try:
                        conv = line.split(':')[1].strip()
                        data['conviction'] = float(conv.split('/')[0])
                    except:
                        pass
                    break
        
        # Parse position size
        if 'Position Size:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Position Size:' in line:
                    try:
                        size = line.split(':')[1].strip()
                        data['position_size'] = float(size.replace('%', ''))
                    except:
                        pass
                    break
        
        # Parse fair value
        if 'Fair Value:' in cio_text or 'CIO Fair Value:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Fair Value:' in line or 'CIO Fair Value:' in line:
                    try:
                        val = line.split('$')[1].strip().split()[0]
                        data['fair_value'] = float(val.replace(',', ''))
                    except:
                        pass
                    break
        
        # Parse upside
        if 'Upside:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Upside:' in line:
                    try:
                        up = line.split(':')[1].strip()
                        data['upside_percent'] = float(up.replace('%', '').replace('+', ''))
                    except:
                        pass
                    break
        
        # Parse composite score
        if 'Composite Score:' in cio_text:
            for line in cio_text.split('\n'):
                if 'Composite Score:' in line:
                    try:
                        score = line.split(':')[1].strip()
                        data['composite_score'] = float(score.split('/')[0])
                    except:
                        pass
                    break
    
    # Extract from individual agents
    value_analysis = analyzer.results.get('value_analysis', {}).get('full_analysis', '')
    if value_analysis:
        # Extract quality score
        if 'Quality Score:' in value_analysis:
            for line in value_analysis.split('\n'):
                if 'Quality Score:' in line and '/10' in line:
                    try:
                        score = line.split(':')[1].strip()
                        data['quality_score'] = float(score.split('/')[0])
                    except:
                        pass
                    break
        
        # Extract moat rating
        if 'Moat' in value_analysis:
            for line in value_analysis.split('\n'):
                if 'Moat Strength' in line or 'YOUR RATING' in line:
                    if 'STRONG' in line.upper():
                        data['moat_rating'] = 'Strong'
                    elif 'MEDIUM' in line.upper():
                        data['moat_rating'] = 'Medium'
                    elif 'WEAK' in line.upper():
                        data['moat_rating'] = 'Weak'
                    break
        
        # Extract value recommendation
        if 'RECOMMENDATION:' in value_analysis:
            for line in value_analysis.split('\n'):
                if line.strip().startswith('**RECOMMENDATION'):
                    data['value_rec'] = line.split(':')[1].strip().split()[0]
                    break
    
    risk_analysis = analyzer.results.get('risk_analysis', {}).get('full_analysis', '')
    if risk_analysis:
        # Extract risk score
        if 'Risk Score:' in risk_analysis:
            for line in risk_analysis.split('\n'):
                if 'Risk Score:' in line and '/10' in line:
                    try:
                        score = line.split(':')[1].strip()
                        data['risk_score'] = float(score.split('/')[0])
                    except:
                        pass
                    break
        
        # Extract risk rating
        if 'RISK RATING:' in risk_analysis or 'Risk Rating:' in risk_analysis:
            for line in risk_analysis.split('\n'):
                if 'Risk Rating:' in line or 'RISK RATING:' in line:
                    rating = line.split(':')[1].strip()
                    data['risk_rating'] = rating.split('(')[0].strip()
                    break
    
    return data
