import streamlit as st
import openai
from datetime import datetime
import re
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_openai_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            api_key = None
    return api_key

st.set_page_config(page_title="Forex Script Generator", page_icon="💱", layout="wide")

class ForexScriptGenerator:
    def __init__(self):
        self.forex_categories = {
            'educational': {
                'name': '📚 Educational Content',
                'description': 'Professional forex education and market analysis',
                'tone': 'professional, educational, trustworthy',
                'cta_style': 'Learning-focused CTA',
                'examples': 'How to read candlesticks, What is leverage'
            },
            'news_analysis': {
                'name': '📰 News & Market Analysis', 
                'description': 'Current market events and insights',
                'tone': 'analytical, timely, authoritative',
                'cta_style': 'Opinion/discussion CTA',
                'examples': 'Fed decision impact, NFP data reaction'
            },
            'raw_stories': {
                'name': '🎭 Raw Trading Stories',
                'description': 'Honest trading experiences with humor',
                'tone': 'conversational, vulnerable, story-driven',
                'cta_style': 'Relatable community CTA',
                'examples': 'How I lost $500 in 4 seconds, My worst FOMO trade'
            },
            'viral_content': {
                'name': '🔥 Viral & Trending',
                'description': 'Social media trends and memes',
                'tone': 'trendy, energetic, social media savvy',
                'cta_style': 'Engagement/challenge CTA',
                'examples': 'POV: You\'re a forex trader'
            }
        }

    def generate_script(self, input_text, input_type, category, script_length):
        openai_key = get_openai_key()
        if not openai_key:
            return {'success': False, 'error': 'No API key found'}
        
        try:
            client = openai.OpenAI(api_key=openai_key)
            
            word_counts = {
                '15s': {'total': 35, 'hook': 8, 'body': 20, 'cta': 7},
                '30s': {'total': 75, 'hook': 15, 'body': 45, 'cta': 15},
                '60s': {'total': 150, 'hook': 25, 'body': 100, 'cta': 25}
            }
            
            target_counts = word_counts[script_length]
            category_info = self.forex_categories[category]
            
            if input_type == "Title/Topic":
                prompt_context = f"Topic: {input_text}"
            elif input_type == "CTA":
                prompt_context = f"CTA: {input_text}"
            else:
                prompt_context = f"Hook: {input_text}"
            
            system_prompt = f"""
            Create a forex video script.
            Category: {category_info['name']}
            Tone: {category_info['tone']}
            
            SPECIAL FOR RAW STORIES:
            If this is "Raw Trading Stories", write like telling a friend a real story:
            - Show emotional journey: careful → bored → impulsive → regret
            - Use natural speech: "Spent 4 hours building position. Result? +$5. Cool. Whatever."
            - Include internal dialogue: "Quick win," I told myself
            - Be vulnerable about mistakes
            
            Target words: Hook {target_counts['hook']}, Body {target_counts['body']}, CTA {target_counts['cta']}
            """
            
            user_prompt = f"""
            {prompt_context}
            
            Create a {script_length} video script.
            
            Format:
            **HOOK:**
            [hook text]
            
            **BODY:**
            [body text]
            
            **CTA:**
            [cta text]
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            script_text = response.choices[0].message.content.strip()
            script_parts = self.parse_script(script_text)
            
            # Calculate word counts
            hook_words = len(script_parts['hook'].split()) if script_parts['hook'] else 0
            body_words = len(script_parts['body'].split()) if script_parts['body'] else 0
            cta_words = len(script_parts['cta'].split()) if script_parts['cta'] else 0
            total_words = hook_words + body_words + cta_words
            
            return {
                'success': True,
                'script_parts': script_parts,
                'word_counts': {'hook': hook_words, 'body': body_words, 'cta': cta_words, 'total': total_words},
                'target_counts': target_counts
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def transcreate_script(self, script_parts, target_language):
        openai_key = get_openai_key()
        if not openai_key:
            return {'success': False, 'error': 'No API key found'}
        
        try:
            client = openai.OpenAI(api_key=openai_key)
            
            languages = {'th': 'Thai', 'vi': 'Vietnamese', 'zhs': 'Chinese (Simplified)', 'zht': 'Chinese (Traditional)'}
            language_name = languages.get(target_language, target_language)
            
            full_script = f"HOOK: {script_parts['hook']}\n\nBODY: {script_parts['body']}\n\nCTA: {script_parts['cta']}"
            
            prompt = f"""
            Transcreate this English forex video script to {language_name}.
            
            Requirements:
            - Make it natural for spoken video content
            - Adapt culturally for {language_name} audience
            - Keep same emotional impact
            - Maintain forex terms accurately
            
            Original:
            {full_script}
            
            Transcreate maintaining HOOK/BODY/CTA structure.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You transcreate forex content to {language_name} for video."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            transcreated_text = response.choices[0].message.content.strip()
            transcreated_parts = self.parse_script(transcreated_text)
            
            return {'success': True, 'transcreated_parts': transcreated_parts}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def parse_script(self, script_text):
        script_parts = {'hook': '', 'body': '', 'cta': ''}
        
        hook_match = re.search(r'\*\*HOOK:\*\*\s*(.*?)(?=\*\*BODY:\*\*|$)', script_text, re.DOTALL | re.IGNORECASE)
        body_match = re.search(r'\*\*BODY:\*\*\s*(.*?)(?=\*\*CTA:\*\*|$)', script_text, re.DOTALL | re.IGNORECASE)
        cta_match = re.search(r'\*\*CTA:\*\*\s*(.*?)$', script_text, re.DOTALL | re.IGNORECASE)
        
        if hook_match:
            script_parts['hook'] = hook_match.group(1).strip()
        if body_match:
            script_parts['body'] = body_match.group(1).strip()
        if cta_match:
            script_parts['cta'] = cta_match.group(1).strip()
        
        if not any(script_parts.values()):
            script_parts['body'] = script_text
        
        return script_parts

def main():
    st.title("💱 Forex Script Generator")
    
    generator = ForexScriptGenerator()
    
    # Check API key
    openai_key = get_openai_key()
    if not openai_key:
        st.error("❌ OpenAI API key required")
        st.info("Add OPENAI_API_KEY to .env file or Streamlit secrets")
        return
    
    # Tabs
    tab1, tab2 = st.tabs(["📝 Generate Script", "🌍 Transcreation"])
    
    with tab1:
        # Input
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_type = st.radio("Start with:", ["Title/Topic", "Hook", "CTA"], horizontal=True)
            
            input_text = st.text_area(
                f"Enter {input_type}:",
                height=100,
                placeholder="e.g., How I lost $500 in 4 seconds"
            )
        
        with col2:
            category = st.selectbox(
                "Content Type:",
                options=list(generator.forex_categories.keys()),
                format_func=lambda x: generator.forex_categories[x]['name']
            )
            
            script_length = st.selectbox("Length:", ["15s", "30s", "60s"], index=1)
        
        # Generate
        if st.button("🚀 Generate", type="primary", disabled=not input_text):
            with st.spinner("Generating..."):
                result = generator.generate_script(input_text, input_type, category, script_length)
            
            if result['success']:
                st.session_state.script = result
                st.success("✅ Generated!")
            else:
                st.error(f"❌ {result['error']}")
        
        # Show script
        if 'script' in st.session_state:
            script_data = st.session_state.script
            script_parts = script_data['script_parts']
            word_counts = script_data['word_counts']
            
            st.divider()
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Words", word_counts['total'])
            col2.metric("Hook", word_counts['hook'])
            col3.metric("Body", word_counts['body'])
            col4.metric("CTA", word_counts['cta'])
            
            # Script
            st.text_area("🎣 HOOK", script_parts['hook'], height=80, key="hook_display")
            st.text_area("📖 BODY", script_parts['body'], height=150, key="body_display")
            st.text_area("📢 CTA", script_parts['cta'], height=80, key="cta_display")
            
            # Export
            full_script = f"HOOK:\n{script_parts['hook']}\n\nBODY:\n{script_parts['body']}\n\nCTA:\n{script_parts['cta']}"
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download",
                    data=full_script,
                    file_name=f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("📋 Copy"):
                    st.code(full_script)
    
    with tab2:
        if 'script' not in st.session_state:
            st.info("👈 Generate a script first")
            return
        
        st.subheader("🌍 Transcreation")
        
        # Language selection
        languages = {
            'th': '🇹🇭 Thai',
            'vi': '🇻🇳 Vietnamese', 
            'zhs': '🇨🇳 Chinese (Simplified)',
            'zht': '🇹🇼 Chinese (Traditional)'
        }
        
        selected_lang = st.selectbox("Select Language:", list(languages.keys()), format_func=lambda x: languages[x])
        
        if st.button(f"🔄 Transcreate to {languages[selected_lang]}", type="primary"):
            with st.spinner("Transcreating..."):
                script_parts = st.session_state.script['script_parts']
                result = generator.transcreate_script(script_parts, selected_lang)
            
            if result['success']:
                st.session_state[f'transcreation_{selected_lang}'] = result
                st.success("✅ Transcreation complete!")
            else:
                st.error(f"❌ {result['error']}")
        
        # Show transcreation
        transcreation_key = f'transcreation_{selected_lang}'
        if transcreation_key in st.session_state:
            transcreated_parts = st.session_state[transcreation_key]['transcreated_parts']
            
            st.divider()
            st.subheader(f"{languages[selected_lang]} Version")
            
            # Side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**English**")
                script_parts = st.session_state.script['script_parts']
                st.text_area("English Hook", script_parts['hook'], height=80, disabled=True, key="eng_hook")
                st.text_area("English Body", script_parts['body'], height=120, disabled=True, key="eng_body")
                st.text_area("English CTA", script_parts['cta'], height=80, disabled=True, key="eng_cta")
            
            with col2:
                st.markdown(f"**{languages[selected_lang]}**")
                st.text_area("Transcreated Hook", transcreated_parts['hook'], height=80, key=f"trans_hook_{selected_lang}")
                st.text_area("Transcreated Body", transcreated_parts['body'], height=120, key=f"trans_body_{selected_lang}")
                st.text_area("Transcreated CTA", transcreated_parts['cta'], height=80, key=f"trans_cta_{selected_lang}")
            
            # Export transcreation
            trans_script = f"HOOK:\n{transcreated_parts['hook']}\n\nBODY:\n{transcreated_parts['body']}\n\nCTA:\n{transcreated_parts['cta']}"
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    f"📥 Download {languages[selected_lang]}",
                    data=trans_script,
                    file_name=f"script_{selected_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key=f"download_{selected_lang}"
                )
            with col2:
                if st.button(f"📋 Copy {languages[selected_lang]}", key=f"copy_{selected_lang}"):
                    st.code(trans_script)

if __name__ == "__main__":
    main()