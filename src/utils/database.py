# src/utils/database.py

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models.prompt import Base, PromptTemplate

def get_app_data_path():
    """Get the appropriate data directory based on the operating system"""
    if sys.platform == 'win32':
        # Windows: Use AppData/Local
        app_data = os.getenv('LOCALAPPDATA')
        app_dir = os.path.join(app_data, 'PromptingHelper')
    elif sys.platform == 'darwin':
        # macOS: Use Application Support
        home = os.path.expanduser('~')
        app_dir = os.path.join(home, 'Library', 'Application Support', 'PromptingHelper')
    else:
        # Linux: Use .local/share
        home = os.path.expanduser('~')
        app_dir = os.path.join(home, '.local', 'share', 'PromptingHelper')
    
    # Create directory if it doesn't exist
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

class Database:
    def __init__(self, db_path=None):
        """Initialize database connection and create tables"""
        if db_path is None:
            # Use platform-appropriate data directory
            app_data_dir = get_app_data_path()
            db_path = os.path.join(app_data_dir, 'prompts.db')
        
        self.db_path = db_path
               
        # Create database engine
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False  # Set to True for SQL debugging
        )
        
        # Create all tables defined in models
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize with sample templates if database is new
        if self._is_database_empty():
            self._create_sample_templates()
    
    def _is_database_empty(self):
        """Check if database has any records"""
        session = self.Session()
        try:
            count = session.query(PromptTemplate).count()
            return count == 0
        finally:
            session.close()
    
    def _create_sample_templates(self):
        """Create sample templates for new users"""
        templates = [
            PromptTemplate(
                title="Data Analysis Expert",
                role="Senior Data Scientist with 10+ years experience",
                context="Analyzing sales data for Q3 2025 performance",
                objective="Identify key trends and provide actionable insights",
                style="Professional and analytical",
                tone="Confident yet approachable",
                audience="C-suite executives",
                response_format="Executive summary with bullet points and data visualizations",
                start_analysis="Focus on revenue growth and customer retention metrics",
                is_template=True,
                tags="data analysis,business,templates"
            ),
            PromptTemplate(
                title="Content Writer",
                role="Creative content writer specializing in technology",
                context="Writing blog posts for a SaaS company",
                objective="Create engaging content that drives conversions",
                style="Conversational and informative",
                tone="Friendly and enthusiastic",
                audience="Small business owners and entrepreneurs",
                response_format="Blog post with introduction, 3-5 main points, and conclusion",
                start_analysis="Begin with a compelling hook about common pain points",
                is_template=True,
                tags="content writing,marketing,templates"
            )
        ]
        
        session = self.Session()
        try:
            for template in templates:
                session.add(template)
            session.commit()
        finally:
            session.close()
    
    # CREATE operations
    def save_prompt(self, prompt):
        """Save a new prompt to database"""
        session = self.Session()
        try:
            session.add(prompt)
            session.commit()
            session.refresh(prompt)  # Get the assigned ID
            return prompt.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # READ operations
    def get_all_prompts(self, include_templates=True):
        """Get all prompts, optionally excluding templates"""
        session = self.Session()
        try:
            query = session.query(PromptTemplate)
            if not include_templates:
                query = query.filter(PromptTemplate.is_template == False)
            return query.order_by(desc(PromptTemplate.created_at)).all()
        finally:
            session.close()
    
    def get_prompt(self, prompt_id):
        """Get a specific prompt by ID"""
        session = self.Session()
        try:
            return session.query(PromptTemplate).filter_by(id=prompt_id).first()
        finally:
            session.close()
    
    def get_templates(self):
        """Get only template prompts"""
        session = self.Session()
        try:
            return session.query(PromptTemplate)\
                .filter(PromptTemplate.is_template == True)\
                .order_by(PromptTemplate.title)\
                .all()
        finally:
            session.close()
    
    def get_favorites(self):
        """Get favorite/starred prompts"""
        session = self.Session()
        try:
            return session.query(PromptTemplate)\
                .filter(PromptTemplate.is_favorite == True)\
                .order_by(desc(PromptTemplate.updated_at))\
                .all()
        finally:
            session.close()
    
    def search_prompts(self, search_term):
        """Search prompts by title, tags, or any COSTAR field"""
        session = self.Session()
        try:
            search_pattern = f"%{search_term}%"
            return session.query(PromptTemplate).filter(
                (PromptTemplate.title.ilike(search_pattern)) |
                (PromptTemplate.role.ilike(search_pattern)) |
                (PromptTemplate.context.ilike(search_pattern)) |
                (PromptTemplate.objective.ilike(search_pattern)) |
                (PromptTemplate.tags.ilike(search_pattern))
            ).all()
        finally:
            session.close()
    
    # UPDATE operations
    def update_prompt(self, prompt_id, **kwargs):
        """Update specific fields of a prompt"""
        session = self.Session()
        try:
            prompt = session.query(PromptTemplate).filter_by(id=prompt_id).first()
            if prompt:
                for key, value in kwargs.items():
                    if hasattr(prompt, key):
                        setattr(prompt, key, value)
                prompt.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def toggle_favorite(self, prompt_id):
        """Toggle favorite status of a prompt"""
        session = self.Session()
        try:
            prompt = session.query(PromptTemplate).filter_by(id=prompt_id).first()
            if prompt:
                prompt.is_favorite = not prompt.is_favorite
                session.commit()
                return prompt.is_favorite
            return None
        finally:
            session.close()
    
    def increment_usage(self, prompt_id):
        """Increment usage count and update last_used_at"""
        session = self.Session()
        try:
            prompt = session.query(PromptTemplate).filter_by(id=prompt_id).first()
            if prompt:
                prompt.usage_count += 1
                prompt.last_used_at = datetime.now()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # DELETE operations
    def delete_prompt(self, prompt_id):
        """Delete a prompt by ID"""
        session = self.Session()
        try:
            prompt = session.query(PromptTemplate).filter_by(id=prompt_id).first()
            if prompt:
                session.delete(prompt)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # UTILITY operations
    def get_statistics(self):
        """Get database statistics"""
        session = self.Session()
        try:
            total = session.query(PromptTemplate).count()
            templates = session.query(PromptTemplate)\
                .filter(PromptTemplate.is_template == True).count()
            favorites = session.query(PromptTemplate)\
                .filter(PromptTemplate.is_favorite == True).count()
            
            return {
                "total_prompts": total,
                "templates": templates,
                "user_prompts": total - templates,
                "favorites": favorites
            }
        finally:
            session.close()
    
    def export_to_json(self, filepath):
        """Export all prompts to JSON file"""
        import json
        session = self.Session()
        try:
            prompts = session.query(PromptTemplate).all()
            data = [prompt.to_dict() for prompt in prompts]
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
        finally:
            session.close()
    
    def import_from_json(self, filepath):
        """Import prompts from JSON file"""
        import json
        session = self.Session()
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for item in data:
                # Remove id to let database assign new ones
                item.pop('id', None)
                # Convert ISO format strings back to datetime
                if item.get('created_at'):
                    item['created_at'] = datetime.fromisoformat(item['created_at'])
                if item.get('updated_at'):
                    item['updated_at'] = datetime.fromisoformat(item['updated_at'])
                if item.get('last_used_at') and item['last_used_at']:
                    item['last_used_at'] = datetime.fromisoformat(item['last_used_at'])
                
                # Convert tags list back to comma-separated string
                if isinstance(item.get('tags'), list):
                    item['tags'] = ",".join(item['tags'])
                
                prompt = PromptTemplate(**item)
                session.add(prompt)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Import error: {e}")
            return False
        finally:
            session.close()

