#!/usr/bin/env python3
"""
Canvas LMS Assignment Submissions Downloader

This script downloads all student submissions for a specific assignment
using the Canvas REST API.

Requirements:
- requests library: pip install requests
- Canvas API token with appropriate permissions
- Course ID and Assignment ID

Usage:
    python canvas_downloader.py
"""

import requests
from pprint import pprint
import json
from pathlib import Path
from urllib.parse import urlparse
import time

# _BASE_URL   = "https://colorado.instructure.com"
_BASE_URL   = "https://canvas.instructure.com/api/v1/"
# _BASE_URL   = "https://colorado.instructure.com/api/v1/"
_TOKEN_FILE = "secrets/canvas.json"
_COURSE_ID  = "122404"


class CanvasManager:
    """ Handles communication with Canvas LMS (Instructure) """

    def __init__( self, canvas_url = _BASE_URL, token_path = _TOKEN_FILE, courseID = _COURSE_ID ):
        """
        Initialize the Canvas API client.
        
        Args:
            canvas_url (str): Base URL for Canvas instance (e.g., 'https://school.instructure.com')
            api_token (str): Canvas API access token
        """
        self.secret = dict()
        with open( token_path, 'r' ) as f:
            self.secret = json.load( f )
        self.canvas_url = canvas_url.rstrip('/')
        self.api_token  = self.secret['token']
        self.session    = requests.Session()
        self.session.headers.update( {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        } )
        self.courseID = courseID


    def get_students( self ):
        url = f"{self.canvas_url}/courses/{self.courseID}/enrollments"
        print( url )
        params = {
            'type[]': ['StudentEnrollment',],
            'state[]': ['active',],
            'include[]': ['uuid','current_points','group_ids',],
            # 'per_page': 100  # Maximum allowed per page
        }
        response = self.session.get( url, params=params )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch submissions: {response.status_code} - {response.text}")
        data = response.json()
        pprint( data )


    def get_submissions( self, assignment_id ):
        """
        Fetch all submissions for a specific assignment.
        
        Args:
            course_id (str): Canvas course ID
            assignment_id (str): Canvas assignment ID
            
        Returns:
            list: List of submission objects
        """
        # url = f"{self.canvas_url}/api/v1/courses/{self.courseID}/assignments/{assignment_id}/submissions"
        url = f"{self.canvas_url}/{self.courseID}/assignments/{assignment_id}/"
        
        # Include submission history, comments, and attachments
        params = {
            'include[]': ['submission_history', 'submission_comments', 'user', 'attachments'],
            'per_page': 100  # Maximum allowed per page
        }
        
        submissions = []
        
        print(f"Fetching submissions for assignment {assignment_id}...")
        
        while url:
            response = self.session.get( url, params=params )
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch submissions: {response.status_code} - {response.text}")
            
            data = response.json()
            submissions.extend(data)
            
            # Handle pagination
            url = None
            if 'Link' in response.headers:
                links = response.headers['Link'].split(',')
                for link in links:
                    if 'rel="next"' in link:
                        url = link.split('<')[1].split('>')[0]
                        params = {}  # Clear params for subsequent requests
                        break
        
        pprint( submissions )
        print(f"Found {len(submissions)} submissions")
        return submissions
    
if __name__ == "__main__":
    cm = CanvasManager()
    cm.get_students()
    # cm.get_submissions( "2429883" )