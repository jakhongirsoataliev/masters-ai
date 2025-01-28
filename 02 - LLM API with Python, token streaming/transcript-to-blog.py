import os
from openai import OpenAI
from pathlib import Path
import logging
from typing import Optional
import sys

class TranscriptToBlogConverter:
    """Converts transcript files to blog posts using OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the converter with OpenAI API credentials.
        
        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY environment variable.
        """
        self.client = OpenAI(api_key=api_key)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the converter."""
        logger = logging.getLogger('TranscriptConverter')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        
        return logger
    
    def read_transcript(self, file_path: str) -> str:
        """
        Read the transcript file content.
        
        Args:
            file_path: Path to the transcript file.
            
        Returns:
            The content of the transcript file.
            
        Raises:
            FileNotFoundError: If the transcript file doesn't exist.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error(f"Transcript file not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading transcript file: {str(e)}")
            raise

    def generate_blog_post(self, transcript: str, model: str = "gpt-4") -> str:
        """
        Generate a blog post from the transcript using OpenAI's API.
        
        Args:
            transcript: The transcript content.
            model: The OpenAI model to use.
            
        Returns:
            Generated blog post content.
        """
        try:
            prompt = """Create a well-structured blog post from this transcript.
            Requirements:
            - Include a table of contents
            - Keep it medium length (suitable for social media)
            - Use clear headings and subheadings
            - Format in markdown
            - Focus on key insights and main points
            - Include a brief conclusion
            
            Please provide only the markdown content without any additional text or formatting instructions."""

            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional blog writer and editor."},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": transcript}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            return completion.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error generating blog post: {str(e)}")
            raise

    def save_blog_post(self, content: str, output_path: str) -> None:
        """
        Save the generated blog post to a file.
        
        Args:
            content: The blog post content.
            output_path: Path where the blog post should be saved.
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.logger.info(f"Blog post saved successfully to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving blog post: {str(e)}")
            raise

    def convert(self, input_path: str, output_path: str, model: str = "gpt-4") -> None:
        """
        Convert a transcript file to a blog post.
        
        Args:
            input_path: Path to the transcript file.
            output_path: Path where the blog post should be saved.
            model: The OpenAI model to use.
        """
        try:
            self.logger.info(f"Starting conversion of transcript: {input_path}")
            
            transcript = self.read_transcript(input_path)
            blog_content = self.generate_blog_post(transcript, model)
            self.save_blog_post(blog_content, output_path)
            
            self.logger.info("Conversion completed successfully")
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            raise

def main():
    """Main entry point for the script."""
    # Example usage
    converter = TranscriptToBlogConverter()
    
    try:
        converter.convert(
            input_path="lesson-1-transcript.txt",
            output_path="blog-post.md",
            model="gpt-4"
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
