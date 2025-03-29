import praw
from transformers import pipeline
import gradio as gr
import plotly.express as px
from wordcloud import WordCloud

# Reddit API configuration
CLIENT_ID = "-jg1lvjCoy1osQXFAJ7tYQ"
CLIENT_SECRET = "BC4xZaxw5O1O2XBMkeJBcuPTLpHljQ"
USER_AGENT = "sentiment_tool by Researcher-726"

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
)

sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_text_sentiment(text):
    try:
        result = sentiment_analyzer(text)[0]
        return (1 if result['label'] == "POSITIVE" else 
               -1 if result['label'] == "NEGATIVE" else 0 ), round(result['score'], 2)
    except:
        return 0, 0

def analyze_community_posts(community, post_count=10):
    results = []
    polarities = []
    text_data = []
    
    try:
        subreddit = reddit.subreddit(community)
        posts = list(subreddit.hot(limit=post_count))
        
        for post in posts:
            title_polarity, _ = analyze_text_sentiment(post.title)
            polarities.append(title_polarity)
            text_data.append(post.title)
            
            comment_polarities = []
            post.comments.replace_more(limit=0)
            
            for comment in post.comments[:5]:
                c_polarity, _ = analyze_text_sentiment(comment.body)
                polarities.append(c_polarity)
                text_data.append(comment.body)
                comment_polarities.append(c_polarity)
                
            avg_comment = sum(comment_polarities)/len(comment_polarities) if comment_polarities else 0
            results.append({
                "post": post.title,
                "title_score": title_polarity,
                "comment_avg": avg_comment
            })
            
        positive = sum(1 for p in polarities if p > 0)
        neutral = sum(1 for p in polarities if p == 0)
        negative = sum(1 for p in polarities if p < 0)
        
        cloud = WordCloud(width=800, height=400, 
                        background_color="white").generate(" ".join(text_data))
        
        return {
            "community": community,
            "sentiment_counts": {"pos": positive, "neu": neutral, "neg": negative},
            "post_details": results,
            "word_cloud": cloud
        }
    except Exception as e:
        return {"error": str(e)}

def check_market_sentiment(company, post_count=10):
    results = []
    polarities = []
    
    try:
        posts = list(reddit.subreddit("all").search(company, limit=post_count))
        
        for post in posts:
            title_polarity, _ = analyze_text_sentiment(post.title)
            polarities.append(title_polarity)
            
            comment_polarities = []
            post.comments.replace_more(limit=0)
            
            for comment in post.comments[:5]:
                c_polarity, _ = analyze_text_sentiment(comment.body)
                polarities.append(c_polarity)
                comment_polarities.append(c_polarity)
                
            avg_comment = sum(comment_polarities)/len(comment_polarities) if comment_polarities else 0
            results.append({
                "post": post.title,
                "title_score": title_polarity,
                "comment_avg": avg_comment
            })
            
        positive = sum(1 for p in polarities if p > 0)
        neutral = sum(1 for p in polarities if p == 0)
        negative = sum(1 for p in polarities if p < 0)
        
        return {
            "company": company,
            "sentiment_counts": {"pos": positive, "neu": neutral, "neg": negative},
            "post_details": results
        }
    except:
        return {"error": "Analysis failed"}

def evaluate_product_mentions(product, post_count=10):
    results = []
    polarities = []
    
    try:
        posts = list(reddit.subreddit("all").search(product, limit=post_count))
        
        for post in posts:
            title_polarity, _ = analyze_text_sentiment(post.title)
            polarities.append(title_polarity)
            
            comment_polarities = []
            post.comments.replace_more(limit=0)
            
            for comment in post.comments[:5]:
                c_polarity, _ = analyze_text_sentiment(comment.body)
                polarities.append(c_polarity)
                comment_polarities.append(c_polarity)
                
            avg_comment = sum(comment_polarities)/len(comment_polarities) if comment_polarities else 0
            results.append({
                "post": post.title,
                "title_score": title_polarity,
                "comment_avg": avg_comment
            })
            
        positive = sum(1 for p in polarities if p > 0)
        neutral = sum(1 for p in polarities if p == 0)
        negative = sum(1 for p in polarities if p < 0)
        
        return {
            "product": product,
            "sentiment_counts": {"pos": positive, "neu": neutral, "neg": negative},
            "post_details": results
        }
    except:
        return {"error": "Analysis failed"}

def scan_suspicious_links(community, keyword=None, post_count=10):
    findings = []
    
    try:
        subreddit = reddit.subreddit(community)
        posts = list(subreddit.hot(limit=post_count))
        
        for post in posts:
            suspicious = []
            
            if "http" in post.title.lower() or "http" in post.selftext.lower():
                suspicious.append(post.url)
                
            post.comments.replace_more(limit=0)
            for comment in post.comments[:5]:
                if "http" in comment.body.lower():
                    suspicious.append(comment.body)
                    
            if keyword:
                suspicious = [link for link in suspicious if keyword.lower() in link.lower()]
                
            if suspicious:
                findings.append([post.title, ", ".join(suspicious)])
                
        return findings if findings else [["No suspicious links found"]]
    except:
        return [["Analysis error"]]

with gr.Blocks(css="""
    .gradio-container {max-width: 1200px; margin: 0 auto; padding: 2rem;}
    .center {text-align: center;}
    .output-section {margin: 2rem 0; padding: 1rem; background: #f8f9fa; border-radius: 8px;}
    .gr-textbox {width: 80% !important; margin: 0 auto;}
    .gr-number {width: 150px !important;}
    .gr-button {margin: 1rem auto !important; display: block !important;}
    .gr-plot {border: 1px solid #eee; border-radius: 8px;}
""") as interface:
    
    gr.Markdown("# Social Sentiment Analysis Tool", elem_classes="center")
    
    # Community analysis section
    with gr.Column(elem_classes=["output-section"]):
        gr.Markdown("### social media Sentiment Analysis", elem_classes="center")
        with gr.Row():
            community_input = gr.Textbox(placeholder="enter topic Sentiment Analysis (eg:love)", elem_classes="center")
            post_count_input = gr.Number(value=10, minimum=1, maximum=50)
        analyze_btn = gr.Button("Analyze Community", variant="primary")
        with gr.Row():
            sentiment_plot = gr.Plot()
            post_plot = gr.Plot()
            cloud_plot = gr.Plot()
            
    # Market analysis section
    with gr.Column(elem_classes=["output-section"]):
        gr.Markdown("### Stock Market Sentiment Analysis", elem_classes="center")
        with gr.Row():
            company_input = gr.Textbox(placeholder="Enter company name eg:adani")
            market_post_count = gr.Number(value=10, minimum=1, maximum=50)
        market_btn = gr.Button("Analyze Market Sentiment", variant="secondary")
        market_output = gr.DataFrame(headers=["Company", "Positive", "Neutral", "Negative"])
        
    # Product analysis section
    with gr.Column(elem_classes=["output-section"]):
        gr.Markdown("### Product Feedback Analysis (eg: iphone15)", elem_classes="center")
        with gr.Row():
            product_input = gr.Textbox(placeholder="Enter product name with model")
            product_post_count = gr.Number(value=10, minimum=1, maximum=50)
        product_btn = gr.Button("Analyze Product Feedback", variant="secondary")
        product_output = gr.DataFrame(headers=["Product", "Positive", "Neutral", "Negative"])
        
    # Link scanner section
    with gr.Column(elem_classes=["output-section"]):
        gr.Markdown("###  safe Link Security Scanner", elem_classes="center")
        with gr.Row():
            scan_community = gr.Textbox(placeholder="Enter community name")
            scan_keyword = gr.Textbox(placeholder="Optional keyword")
            scan_count = gr.Number(value=10, minimum=1, maximum=50)
        scan_btn = gr.Button("Scan for Threats", variant="secondary")
        scan_output = gr.DataFrame(headers=["Post Title", "Suspicious Links"])
        
    # Visualization functions
    def generate_sentiment_pie(data):
        labels = ['Positive', 'Neutral', 'Negative']
        colors = ['#2ecc71', '#f1c40f', '#e74c3c']
        return px.pie(values=[data['pos'], data['neu'], data['neg']], 
                     names=labels, 
                     color_discrete_sequence=colors,
                     hole=0.3)
                     
    def generate_post_bar(data):
        titles = [p['post'] for p in data]
        titles_score = [p['title_score'] for p in data]
        comments_avg = [p['comment_avg'] for p in data]
        return px.bar(x=titles, y=[titles_score, comments_avg], 
                     barmode='group', 
                     labels={'x': 'Posts', 'y': 'Sentiment'},
                     color_discrete_sequence=['#3498db', '#9b59b6'])
                     
    def generate_cloud(wordcloud):
        return px.imshow(wordcloud)
        
    # Interface handlers
    def handle_community_analysis(community, count):
        result = analyze_community_posts(community, count)
        if "error" in result:
            return [gr.update(visible=False)]*3
            
        pie = generate_sentiment_pie(result['sentiment_counts'])
        bar = generate_post_bar(result['post_details'])
        cloud = generate_cloud(result['word_cloud'])
        return pie, bar, cloud
        
    def handle_market_analysis(company, count):
        result = check_market_sentiment(company, count)
        if "error" in result:
            return gr.update(value=[["Error: No data found"]])
            
        return [[result['company'], 
                result['sentiment_counts']['pos'],
                result['sentiment_counts']['neu'],
                result['sentiment_counts']['neg']]]
                
    def handle_product_analysis(product, count):
        result = evaluate_product_mentions(product, count)
        if "error" in result:
            return gr.update(value=[["Error: No data found"]])
            
        return [[result['product'], 
                result['sentiment_counts']['pos'],
                result['sentiment_counts']['neu'],
                result['sentiment_counts']['neg']]]
                
    def handle_link_scan(community, keyword, count):
        return scan_suspicious_links(community, keyword, count)
        
    # Event bindings
    analyze_btn.click(
        handle_community_analysis,
        inputs=[community_input, post_count_input],
        outputs=[sentiment_plot, post_plot, cloud_plot]
    )
    
    market_btn.click(
        handle_market_analysis,
        inputs=[company_input, market_post_count],
        outputs=[market_output]
    )
    
    product_btn.click(
        handle_product_analysis,
        inputs=[product_input, product_post_count],
        outputs=[product_output]
    )
    
    scan_btn.click(
        handle_link_scan,
        inputs=[scan_community, scan_keyword, scan_count],
        outputs=[scan_output]
    )

interface.launch(share=True)