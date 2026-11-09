import sqlite3
from pathlib import Path
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='AI Smart Wardrobe',page_icon='👔',layout='wide')
ROOT=Path(__file__).resolve().parent
DB=ROOT/'wardrobe.db'
IMAGES=ROOT/'uploads';IMAGES.mkdir(exist_ok=True)
CATEGORIES=['Top','Bottom','Shoes','Outerwear']
OCCASIONS=['Work','University','Casual','Formal','Sports']
STYLES=['Classic','Minimalist','Streetwear','Sporty']
COLORS=['White','Black','Gray','Navy','Blue','Beige','Brown','Green','Red','Pink','Other']

def connect():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def initialize():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS clothes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, color TEXT NOT NULL, style TEXT NOT NULL, occasions TEXT NOT NULL, season TEXT NOT NULL, image TEXT, created_at TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS saved_outfits (id INTEGER PRIMARY KEY AUTOINCREMENT, top_id INTEGER, bottom_id INTEGER, shoes_id INTEGER, occasion TEXT, style TEXT, saved_at TEXT NOT NULL)''')
initialize()

def all_clothes():
    with connect() as c:return [dict(x) for x in c.execute('SELECT * FROM clothes ORDER BY id DESC')]

def add_item(name,category,color,style,occasions,season,image=None):
    with connect() as c:
        c.execute('INSERT INTO clothes (name,category,color,style,occasions,season,image,created_at) VALUES (?,?,?,?,?,?,?,?)',(name.strip(),category,color,style,','.join(occasions),season,image,datetime.now().isoformat(timespec='seconds')))

def delete_item(item_id):
    with connect() as c:c.execute('DELETE FROM clothes WHERE id=?',(item_id,))

# The deterministic scoring engine is intentionally transparent, offline and testable.
NEUTRALS={'White','Black','Gray','Navy','Beige','Brown'}
COLOR_PAIRS={frozenset(x) for x in [('White','Navy'),('White','Blue'),('White','Black'),('White','Beige'),('Black','Gray'),('Black','Blue'),('Navy','Beige'),('Navy','Gray'),('Brown','Beige'),('Green','Beige'),('Blue','Brown'),('Pink','Gray'),('Red','Black'),('Green','Black')]}

def compatible(a,b):
    if a==b:return 2
    if frozenset((a,b)) in COLOR_PAIRS:return 4
    if a in NEUTRALS and b in NEUTRALS:return 3
    if a in NEUTRALS or b in NEUTRALS:return 2
    return 0

def item_score(item,occasion,style,season):
    score=0
    if occasion in item['occasions'].split(','):score+=6
    if item['style']==style:score+=4
    if item['season']=='All seasons' or season=='Any' or item['season']==season:score+=3
    return score

def recommend(items,occasion,style,season='Any',limit=3):
    tops=[x for x in items if x['category']=='Top']
    bottoms=[x for x in items if x['category']=='Bottom']
    shoes=[x for x in items if x['category']=='Shoes']
    results=[]
    for t in tops:
        for b in bottoms:
            for s in shoes:
                score=sum(item_score(x,occasion,style,season) for x in (t,b,s))
                score+=compatible(t['color'],b['color'])+compatible(b['color'],s['color'])+compatible(t['color'],s['color'])
                results.append({'top':t,'bottom':b,'shoes':s,'score':score})
    results.sort(key=lambda x:(-x['score'],x['top']['id'],x['bottom']['id'],x['shoes']['id']))
    return results[:limit]

def seed():
    if all_clothes():return False
    sample=[
    ('White Oxford Shirt','Top','White','Classic',['Work','University','Formal'],'All seasons'),
    ('Black T-Shirt','Top','Black','Minimalist',['Casual','University'],'Summer'),
    ('Navy Polo Shirt','Top','Navy','Classic',['Work','University','Casual'],'All seasons'),
    ('Gray Athletic T-Shirt','Top','Gray','Sporty',['Sports','Casual'],'Summer'),
    ('Beige Chinos','Bottom','Beige','Classic',['Work','University','Casual'],'All seasons'),
    ('Blue Jeans','Bottom','Blue','Minimalist',['Casual','University'],'All seasons'),
    ('Black Dress Pants','Bottom','Black','Classic',['Work','Formal'],'All seasons'),
    ('Black Sports Shorts','Bottom','Black','Sporty',['Sports','Casual'],'Summer'),
    ('Brown Loafers','Shoes','Brown','Classic',['Work','Formal'],'All seasons'),
    ('White Sneakers','Shoes','White','Minimalist',['Casual','University'],'All seasons'),
    ('Black Dress Shoes','Shoes','Black','Classic',['Formal','Work'],'All seasons'),
    ('Gray Running Shoes','Shoes','Gray','Sporty',['Sports','Casual'],'All seasons')]
    for name,cat,color,style,occasions,season in sample:add_item(name,cat,color,style,occasions,season)
    return True

# Modern visual theme. All images are bundled with the app, so hosting requires no image API.
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
html,body,[class*=css],.stApp {font-family:'DM Sans',sans-serif;}
.stApp{background:#f7f8fc;color:#172238;}
[data-testid="stSidebar"]{background:#101d35;}
[data-testid="stSidebar"] *{color:#f2f5ff!important;}
.block-container{max-width:1300px;padding-top:1.25rem;padding-bottom:3rem;}
h1,h2,h3{font-family:'Outfit',sans-serif!important;letter-spacing:-.025em;color:#152440!important;}
h1{font-size:2.35rem!important;}h2{font-size:1.65rem!important;}
[data-testid="stMetric"]{background:#fff;border:1px solid #e6eaf2;padding:20px;border-radius:19px;box-shadow:0 8px 25px rgba(22,40,72,.035);}
[data-testid="stMetricValue"]{color:#16294d;font-weight:750;}
.stButton button[kind="primary"]{background:#5547e8;border-color:#5547e8;color:white;border-radius:11px;font-weight:700;}
.stButton button{border-radius:11px;font-weight:600;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px!important;border-color:#e6eaf2!important;background:#fff;}
.hero{background:linear-gradient(120deg,#142442 0%,#283b77 54%,#6b5dea 100%);color:white;padding:34px 38px;border-radius:24px;box-shadow:0 16px 40px rgba(32,44,95,.15);margin:0 0 22px;}
.hero h1{color:white!important;font-size:2.55rem!important;line-height:1.13;margin:10px 0;}
.hero p{color:#dce3ff;font-size:1rem;max-width:650px;line-height:1.7;}
.eyebrow{font-size:.72rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#b9c4ff;}
.chip{display:inline-block;background:#ffffff22;color:#fff;padding:7px 12px;border:1px solid #ffffff30;border-radius:30px;font-size:.78rem;margin-right:6px;margin-top:12px;}
.section-kicker{color:#7469d9;font-weight:800;letter-spacing:.1em;text-transform:uppercase;font-size:.7rem;margin-top:20px;}
.mini-note{color:#68778f;font-size:.9rem;line-height:1.65;}
.feature{background:white;border:1px solid #e5e9f2;border-radius:17px;padding:18px;min-height:116px;margin:4px 0;}
.feature b{color:#1c2c4b;font-size:1rem;}.feature p{color:#6d7b91;font-size:.83rem;margin:6px 0 0;}
</style>""",unsafe_allow_html=True)
PAGES=['🏠 Dashboard','➕ Add Clothing','👕 My Wardrobe','✨ Outfit Generator','💾 Saved Outfits','ℹ️ About the Project']
if 'nav' not in st.session_state:st.session_state.nav=PAGES[0]
with st.sidebar:
    st.markdown('## ✦ STYLESPACE')
    st.caption('YOUR DIGITAL CLOSET')
    st.divider()
    page=st.radio('Navigation',PAGES,key='nav',label_visibility='collapsed')
    st.divider()
    st.markdown('**✨ Smart styling, made simple**')
    st.caption('Your wardrobe lives in SQLite. Outfit matches use an explainable offline scoring algorithm.')
assets_dir=ROOT/'assets'
items=all_clothes()
with connect() as _c:
    saved_count=_c.execute('SELECT COUNT(*) FROM saved_outfits').fetchone()[0]



if page=='🏠 Dashboard':
    st.markdown("""<div class='hero'><div class='eyebrow'>✦ YOUR PERSONAL STYLE STUDIO</div>
    <h1>Make every outfit<br>feel effortless.</h1>
    <p>Organize what you own, discover combinations you haven't tried, and get dressed with confidence. Your style, thoughtfully curated.</p>
    <span class='chip'>✦ Smart outfit matching</span><span class='chip'>◉ Personal closet</span><span class='chip'>♡ Save your looks</span></div>""",unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    for col,label,val in zip((a,b,c,d),('🧺 CLOSET ITEMS','👕 TOPS','👖 BOTTOMS','♡ SAVED LOOKS'),(len(items),sum(x['category']=='Top' for x in items),sum(x['category']=='Bottom' for x in items),saved_count)):
        col.metric(label,val)
    st.markdown("<div class='section-kicker'>QUICK START</div>",unsafe_allow_html=True)
    st.subheader('What would you like to do?')
    qa,qb,qc=st.columns(3)
    if qa.button('✨ Create an outfit',use_container_width=True,type='primary'):
        st.session_state.nav=PAGES[3];st.rerun()
    if qb.button('＋ Add new clothing',use_container_width=True):
        st.session_state.nav=PAGES[1];st.rerun()
    if qc.button('👕 Explore my closet',use_container_width=True):
        st.session_state.nav=PAGES[2];st.rerun()
    if not items:
        st.info('Your closet is empty. Start with the sample collection or add your own clothes.')
        if st.button('Load 12 sample clothing items',type='primary'):
            seed();st.rerun()
    st.markdown("<div class='section-kicker'>STYLE INSPIRATION</div>",unsafe_allow_html=True)
    st.subheader('Looks worth trying')
    st.caption('Illustrative outfit inspiration · Your actual recommendations are generated from your saved clothes.')
    inspiration=[('Modern essentials','Classic · Work','look_1.png'),('Everyday cool','Minimalist · Casual','look_2.png'),('Easy weekend','Sporty · Casual','look_3.png')]
    cols=st.columns(3)
    for col,(name,desc,img) in zip(cols,inspiration):
        with col:
            st.image(str(assets_dir/img),use_container_width=True)
            st.markdown(f'**{name}**')
            st.caption(desc)
    st.markdown("<div class='section-kicker'>YOUR WARDROBE AT A GLANCE</div>",unsafe_allow_html=True)
    left,right=st.columns([1.25,1])
    with left:
        st.subheader('Recently added')
        if items:
            for x in items[:4]:
                icon={'Top':'👕','Bottom':'👖','Shoes':'👟','Outerwear':'🧥'}.get(x['category'],'✦')
                st.markdown(f"<div class='feature'><b>{icon} {x['name']}</b><p>{x['category']} · {x['color']} · {x['style']}</p></div>",unsafe_allow_html=True)
        else:st.caption('Your newest pieces will appear here.')
    with right:
        st.subheader('How it works')
        st.markdown("""<div class='feature'><b>01 · Build your closet</b><p>Add clothes with colors, occasions, seasons, and optional photos.</p></div>
        <div class='feature'><b>02 · Choose your vibe</b><p>Select an occasion and personal style to get coordinated outfit ideas.</p></div>
        <div class='feature'><b>03 · Keep your favorites</b><p>Save your favorite combinations and revisit them anytime.</p></div>""",unsafe_allow_html=True)
    st.caption('Privacy note: this demo uses a shared local SQLite database. Streamlit Community Cloud storage can reset on restart; do not upload private photos or sensitive information.')

elif page=='➕ Add Clothing':
    st.subheader('Add a new clothing item')
    with st.form('add',clear_on_submit=True):
        name=st.text_input('Item name',placeholder='e.g. White Oxford Shirt')
        c1,c2=st.columns(2)
        category=c1.selectbox('Category',CATEGORIES)
        color=c2.selectbox('Color',COLORS)
        c3,c4=st.columns(2)
        style=c3.selectbox('Style',STYLES)
        season=c4.selectbox('Season',['All seasons','Summer','Winter'])
        occasions=st.multiselect('Suitable occasions',OCCASIONS,default=['Casual'])
        photo=st.file_uploader('Optional clothing photo',type=['png','jpg','jpeg','webp'])
        submitted=st.form_submit_button('Save to local database',type='primary')
    if submitted:
        if not name.strip():st.error('Please enter a clothing name.')
        elif not occasions:st.error('Select at least one occasion.')
        else:
            path=None
            if photo:
                import uuid
                from PIL import Image
                try:
                    from io import BytesIO
                    img=Image.open(BytesIO(photo.getvalue())).convert('RGB');img.thumbnail((900,900))
                    path=str(IMAGES/(uuid.uuid4().hex+'.jpg'));img.save(path,quality=85)
                except Exception:st.error('Invalid image file.');st.stop()
            add_item(name,category,color,style,occasions,season,path)
            st.success(f'Saved {name} to SQLite successfully!')

elif page=='👕 My Wardrobe':
    st.subheader('My Wardrobe')
    f1,f2,f3=st.columns([2,1,1])
    search=f1.text_input('Search your clothes',placeholder='Search by name or color...')
    filt=f2.selectbox('Category',['All']+CATEGORIES)
    style_filter=f3.selectbox('Style',['All']+STYLES)
    shown=[x for x in items if (filt=='All' or x['category']==filt) and (style_filter=='All' or x['style']==style_filter) and (not search or search.lower() in (x['name']+' '+x['color']).lower())]
    st.caption(f'{len(shown)} item(s) found')
    if not shown:st.info('No clothing items yet. Add an item or load sample data on the dashboard.')
    for x in shown:
        with st.container(border=True):
            c1,c2,c3=st.columns([1,4,1])
            with c1:
                if x['image'] and Path(x['image']).exists():st.image(x['image'],width=110)
                else:st.markdown({'Top':'👕','Bottom':'👖','Shoes':'👟','Outerwear':'🧥'}[x['category']])
            with c2:
                st.markdown(f"**{x['name']}**")
                st.caption(f"{x['category']} • {x['color']} • {x['style']} • {x['season']} • {x['occasions'].replace(',', ', ')}")
            with c3:
                if st.button('Delete',key=f"del{x['id']}"):
                    delete_item(x['id']);st.rerun()

elif page=='✨ Outfit Generator':
    st.subheader('Find your perfect outfit')
    st.caption('Personalized matching based on the clothes in your wardrobe, occasion, color harmony, and style.')
    a,b,c=st.columns(3)
    occasion=a.selectbox('Occasion',OCCASIONS)
    style=b.selectbox('Personal style',STYLES)
    season=c.selectbox('Season',['Any','Summer','Winter'])
    if st.button('✨ Generate matching outfits',type='primary'):
        st.session_state['recommendations']=recommend(items,occasion,style,season)
        st.session_state['selection']=(occasion,style,season)
    if 'recommendations' in st.session_state:
        results=st.session_state['recommendations']
        if not results:st.warning('Add at least one Top, one Bottom, and one pair of Shoes to generate an outfit.')
        else:
            st.caption('Ranked by occasion suitability, style, season, and color harmony. Recommendations use only saved clothes.')
            for i,r in enumerate(results,1):
                with st.container(border=True):
                    st.markdown(f"### Outfit {i}  ·  Match score {r['score']}")
                    cols=st.columns(3)
                    for col,key,emoji in zip(cols,['top','bottom','shoes'],['👕','👖','👟']):
                        item=r[key]
                        with col:
                            if item['image'] and Path(item['image']).exists():st.image(item['image'],use_container_width=True)
                            else:st.markdown(f"## {emoji}")
                            st.markdown(f"**{item['name']}**")
                            st.caption(f"{item['color']} • {item['style']}")
                    st.info(f"Why this works: This combination is ranked for **{st.session_state['selection'][0]}** and **{st.session_state['selection'][1]}**. The colors {r['top']['color'].lower()}, {r['bottom']['color'].lower()}, and {r['shoes']['color'].lower()} are evaluated for coordination.")
                    if st.button(f'Save Outfit {i}',key=f'save{i}'):
                        with connect() as conn:
                            conn.execute('INSERT INTO saved_outfits (top_id,bottom_id,shoes_id,occasion,style,saved_at) VALUES (?,?,?,?,?,?)',(r['top']['id'],r['bottom']['id'],r['shoes']['id'],st.session_state['selection'][0],st.session_state['selection'][1],datetime.now().isoformat(timespec='seconds')))
                        st.success('Outfit saved to SQLite!')

elif page=='💾 Saved Outfits':
    st.subheader('Saved outfits')
    with connect() as c: saved=[dict(x) for x in c.execute('SELECT * FROM saved_outfits ORDER BY id DESC')]
    if not saved:st.info('Generate an outfit and click Save Outfit to see it here.')
    byid={x['id']:x for x in items}
    for x in saved:
        names=[byid.get(x[k],{}).get('name','Deleted item') for k in ('top_id','bottom_id','shoes_id')]
        with st.container(border=True):
            st.markdown(f"**{x['occasion']} · {x['style']}**")
            st.write(' + '.join(names))
            st.caption(f"Saved {x['saved_at']}")
            if st.button('Remove saved outfit',key=f"out{x['id']}"):
                with connect() as c:c.execute('DELETE FROM saved_outfits WHERE id=?',(x['id'],))
                st.rerun()

else:
    st.subheader('About AI Smart Wardrobe')
    st.write('**Problem:** People waste time deciding what to wear and forget which clothes they own.')
    st.write('**Solution:** A web application that manages clothes in a local SQLite database and suggests matching outfits based on user-selected occasion, style, season, and color.')
    st.write('**AI tool used in development:** ChatGPT helped design the database, generate and review Python code, and create the recommendation logic. The runtime recommendation engine is deterministic, not a generative AI model.')
    st.write('**Technology:** Python, Streamlit, SQLite, Pillow.')
    st.write('**Privacy:** Clothing data is stored locally on the computer running the application; no cloud database is required.')
    st.write('**Live demonstration:** Add an item → view My Wardrobe → choose occasion and style → generate outfits → save a recommendation → view Saved Outfits.')
