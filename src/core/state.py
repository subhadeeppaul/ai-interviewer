# src/core/state.py
from __future__ import annotations
from typing import List, Dict, Optional
from typing_extensions import TypedDict

class InterviewState(TypedDict, total=False):
   
    topic: str                  
    topics: List[str]            
    topic_index: int              

   
    difficulty: str               
    difficulty_counts: Dict[str, int]  
    max_q: int                    

    
    asked: List[Dict]             
    answers: List[str]            
    evals: List[Dict]            
    topic_performance: Dict[str, Dict[str, float]]  

   
    current_q: str
    followup_mode: bool
    done: bool
    question_type: str            

    
    stdin_mode: bool             
