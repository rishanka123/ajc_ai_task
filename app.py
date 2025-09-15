import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from textstat import flesch_reading_ease

def check_grammar(text):
    """Basic grammar checking using regex patterns"""
    errors = 0
    patterns = [
        r'\b(i)\b',  # lowercase 'i' as personal pronoun
        r'\b(their|there|they\'re)\b.*\b(their|there|they\'re)\b',  # common confusion
        r'\b(your|you\'re)\b.*\b(your|you\'re)\b',  # common confusion
        r'\b(its|it\'s)\b.*\b(its|it\'s)\b',  # common confusion
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        errors += len(matches)
    
    return errors, []

def check_punctuation(text):
    """Check punctuation errors"""
    # Count missing punctuation at sentence ends
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    errors = 0
    for sentence in sentences:
        if sentence and not re.search(r'[.!?]$', sentence):
            errors += 1
    
    # Check for proper comma usage (basic check)
    comma_errors = text.count(",,") + text.count(" ,") + text.count(", ")
    
    return errors + comma_errors

def check_capitalization(text):
    """Check capitalization errors"""
    errors = 0
    
    # Check sentence beginnings
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    for sentence in sentences:
        if sentence and not sentence[0].isupper():
            errors += 1
    
    # Check proper nouns (basic implementation)
    proper_nouns = re.findall(r'\b([A-Z][a-z]+)\b', text)
    common_mistakes = ['the', 'and', 'of', 'in', 'to', 'a', 'an']
    for word in proper_nouns:
        if word.lower() in common_mistakes:
            errors += 1
    
    return errors

def check_sentence_formation(text):
    """Evaluate sentence structure and readability"""
    # Calculate readability score
    readability = flesch_reading_ease(text)
    
    # Count very short sentences (potential fragments)
    sentences = re.split(r'[.!?]', text)
    short_sentences = sum(1 for s in sentences if len(s.split()) < 3 and len(s.split()) > 0)
    
    # Count very long sentences (potential run-ons)
    long_sentences = sum(1 for s in sentences if len(s.split()) > 25)
    
    return readability, short_sentences + long_sentences

def calculate_scores(text, grammar_errors, punctuation_errors, capitalization_errors, formation_errors):
    """Calculate scores based on error counts"""
    word_count = len(text.split())
    
    # Normalize errors by word count
    grammar_score = max(0, 40 - (grammar_errors * 40 / max(1, word_count/10)))
    punctuation_score = max(0, 20 - (punctuation_errors * 20 / max(1, word_count/10)))
    capitalization_score = max(0, 20 - (capitalization_errors * 20 / max(1, word_count/10)))
    formation_score = max(0, 20 - (formation_errors * 20 / max(1, word_count/10)))
    
    total_score = grammar_score + punctuation_score + capitalization_score + formation_score
    
    return {
        'Grammar': grammar_score,
        'Punctuation': punctuation_score,
        'Capitalization': capitalization_score,
        'Sentence Formation': formation_score,
        'Total': total_score
    }

def generate_feedback(scores, grammar_errors, punctuation_errors, capitalization_errors, formation_errors):
    """Generate feedback based on scores and errors"""
    feedback = []
    
    if scores['Grammar'] >= 35:
        feedback.append("Excellent grammar usage.")
    elif scores['Grammar'] >= 30:
        feedback.append("Good grammar with minor errors.")
    else:
        feedback.append(f"Grammar needs improvement ({grammar_errors} errors detected).")
    
    if scores['Punctuation'] >= 18:
        feedback.append("Punctuation is used correctly.")
    elif scores['Punctuation'] >= 15:
        feedback.append("Generally good punctuation with some mistakes.")
    else:
        feedback.append(f"Punctuation needs work ({punctuation_errors} errors detected).")
    
    if scores['Capitalization'] >= 18:
        feedback.append("Capitalization is properly applied.")
    elif scores['Capitalization'] >= 15:
        feedback.append("Most capitalization is correct.")
    else:
        feedback.append(f"Capitalization needs attention ({capitalization_errors} errors detected).")
    
    if scores['Sentence Formation'] >= 18:
        feedback.append("Sentences are well-structured and readable.")
    elif scores['Sentence Formation'] >= 15:
        feedback.append("Sentence formation is generally good.")
    else:
        feedback.append(f"Sentence formation could be improved ({formation_errors} issues detected).")
    
    return " ".join(feedback)

def main():
    st.set_page_config(page_title="Text Analysis Tool", page_icon="📝", layout="wide")
    
    st.title("📝 Text Analysis Tool")
    st.write("Evaluate your English writing with AI-powered analysis")
    
    # Input section
    st.header("Enter your text")
    text_input = st.text_area("Paste your English passage here (minimum 50 words):", height=200)
    
    if st.button("Analyze Text"):
        # Validate input
        word_count = len(text_input.split())
        if word_count < 50:
            st.error(f"Input must contain at least 50 words. Current word count: {word_count}")
            return
        
        with st.spinner("Analyzing your text..."):
            # Perform analysis
            grammar_errors, grammar_details = check_grammar(text_input)
            punctuation_errors = check_punctuation(text_input)
            capitalization_errors = check_capitalization(text_input)
            readability, formation_errors = check_sentence_formation(text_input)
            
            # Calculate scores
            scores = calculate_scores(
                text_input, 
                grammar_errors, 
                punctuation_errors, 
                capitalization_errors, 
                formation_errors
            )
            
            # Generate feedback
            feedback = generate_feedback(
                scores, 
                grammar_errors, 
                punctuation_errors, 
                capitalization_errors, 
                formation_errors
            )
            
            # Display results
            st.success("Analysis complete!")
            
            # Overall score
            st.header("Overall Score")
            st.metric("Total Score", f"{scores['Total']:.1f}/100")
            
            # Detailed scores
            st.header("Detailed Analysis")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Grammar", f"{scores['Grammar']:.1f}/40")
            with col2:
                st.metric("Punctuation", f"{scores['Punctuation']:.1f}/20")
            with col3:
                st.metric("Capitalization", f"{scores['Capitalization']:.1f}/20")
            with col4:
                st.metric("Sentence Formation", f"{scores['Sentence Formation']:.1f}/20")
            
            # Visualization
            st.header("Score Breakdown")
            
            categories = ['Grammar', 'Punctuation', 'Capitalization', 'Sentence Formation']
            values = [scores['Grammar'], scores['Punctuation'], 
                     scores['Capitalization'], scores['Sentence Formation']]
            max_values = [40, 20, 20, 20]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9C80E'])
            
            # Add value labels on bars
            for i, (v, mv) in enumerate(zip(values, max_values)):
                ax.text(i, v + 0.5, f"{v:.1f}/{mv}", ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel('Score')
            ax.set_ylim(0, 45)
            ax.set_title('Text Analysis Score Breakdown')
            
            st.pyplot(fig)
            
            # Feedback
            st.header("Feedback")
            st.info(feedback)

if __name__ == "__main__":
    main()