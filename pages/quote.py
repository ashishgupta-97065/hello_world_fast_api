"""Random Quote mini-app page."""
from pages._shell import page


def render_quote() -> str:
    """Return full HTML for /apps/quote with a hardcoded 25-quote JS array."""
    body = """
<div style="max-width:640px;margin:0 auto;text-align:center;padding:2rem 0">
  <h1 style="margin-bottom:2rem">Random Quote</h1>
  <div id="quote-card" style="background:var(--surface);border:1px solid var(--border);
    border-radius:16px;padding:2.5rem;margin-bottom:2rem;transition:opacity 0.2s ease">
    <blockquote id="quote-text"
      style="font-size:1.35rem;font-style:italic;line-height:1.7;margin-bottom:1rem;color:var(--text)">
    </blockquote>
    <cite id="quote-author" style="font-size:0.95rem;color:var(--text-muted);font-style:normal"></cite>
  </div>
  <button class="btn btn-primary" id="next-btn" style="font-size:1rem;padding:0.65rem 1.75rem">Next</button>
</div>
"""
    js = r"""
  const quotes = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "You are never too old to set another goal or to dream a new dream.", "author": "C.S. Lewis"},
    {"text": "To handle yourself, use your head; to handle others, use your heart.", "author": "Eleanor Roosevelt"},
    {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
    {"text": "Whether you think you can or you think you can't, you're right.", "author": "Henry Ford"},
    {"text": "I have learned over the years that when one's mind is made up, this diminishes fear.", "author": "Rosa Parks"},
    {"text": "I alone cannot change the world, but I can cast a stone across the waters to create many ripples.", "author": "Mother Teresa"},
    {"text": "Nothing is impossible, the word itself says 'I'm possible'!", "author": "Audrey Hepburn"},
    {"text": "The question isn't who is going to let me; it's who is going to stop me.", "author": "Ayn Rand"},
    {"text": "You become what you believe.", "author": "Oprah Winfrey"},
    {"text": "The most difficult thing is the decision to act; the rest is merely tenacity.", "author": "Amelia Earhart"},
    {"text": "How wonderful it is that nobody need wait a single moment before starting to improve the world.", "author": "Anne Frank"},
    {"text": "An unexamined life is not worth living.", "author": "Socrates"},
    {"text": "Spread love everywhere you go. Let no one ever come to you without leaving happier.", "author": "Mother Teresa"},
    {"text": "When you reach the end of your rope, tie a knot in it and hang on.", "author": "Franklin D. Roosevelt"},
    {"text": "Always remember that you are absolutely unique. Just like everyone else.", "author": "Margaret Mead"},
    {"text": "Do not go where the path may lead; go instead where there is no path and leave a trail.", "author": "Ralph Waldo Emerson"},
    {"text": "You will face many defeats in life, but never let yourself be defeated.", "author": "Maya Angelou"},
    {"text": "The greatest glory in living lies not in never falling, but in rising every time we fall.", "author": "Nelson Mandela"}
  ];

  const card   = document.getElementById('quote-card');
  const textEl = document.getElementById('quote-text');
  const authEl = document.getElementById('quote-author');
  const nextBtn = document.getElementById('next-btn');

  function showQuote(q) {
    card.style.opacity = '0';
    setTimeout(() => {
      textEl.textContent = '“' + q.text + '”';
      authEl.textContent = '— ' + q.author;
      card.style.opacity = '1';
    }, 200);
  }

  function pickRandom() {
    return quotes[Math.floor(Math.random() * quotes.length)];
  }

  nextBtn.onclick = () => showQuote(pickRandom());
  showQuote(pickRandom());
"""
    return page("Random Quote", body, extra_js=js)
