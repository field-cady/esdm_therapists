import streamlit as st
import pydeck as pdk
import json
import pandas as pd

# Page config
st.set_page_config(
    page_title="Contact Map",
    page_icon="📍",
    layout="wide"
)

@st.cache_data
def load_contacts():
    """Load contact data from JSON lines file"""
    df = pd.read_csv('data_w_latlon.tsv', sep='\t')
    return df.to_dict(orient='records')

def aggregate_by_location(contacts):
    """Group contacts by location"""
    location_dict = {}
    
    for contact in contacts:
        lat = contact['lat']
        lon = contact['lon']
        key = (lat, lon)
        
        if key not in location_dict:
            location_dict[key] = {
                'lat': lat,
                'lon': lon,
                'city': contact['City']+', '+contact['State']+', '+contact['Country'],
                'people': []
            }
        
        location_dict[key]['people'].append({
            'name': contact.get('First Name', '') + ' ' + contact.get('Last Name', ''),
            'email': contact.get('Email', ''),
            'degree': contact.get('Degree', '')
        })
    
    return list(location_dict.values())

def create_tooltip_html(loc):
    """Create HTML tooltip for a location with multiple people"""
    html_parts = ['<div style="font-family: Arial; font-size: 14px;">']
    html_parts.append(loc["city"])
    html_parts.append('</div>')
    
    html_parts.append('<div style="font-family: Arial; font-size: 14px;">')

    people = loc['people']
    
    for i, person in enumerate(people):
        if i > 0:
            html_parts.append('<hr style="margin: 8px 0;">')
        
        html_parts.append(f'<b>{person["name"]}</b><br>')
        if person['degree']:
            html_parts.append(f'🎓 {person["degree"]}<br>')        
        if person['email']:
            html_parts.append(f'📧 {person["email"]}<br>')
    
    html_parts.append('</div>')
    return ''.join(html_parts)

def main():
    st.title("📍 ESDM Therapists")

    st.markdown(
        "ESDM (Early Start Denver Model) is a play-based therapy for children on the autism spectrum.  "
        "This app is designed to help you find providers."
    )
    
    st.markdown(
        "Click on any marker to see contact information for providers in that city.  "
        "This data was pulled from the [ESDM website](https://www.esdm.co/esdm-therapists).  "
        "It was made by Field Cady (field.cady@gmail.com) to help other autism parents find  "
        "resources for their children.  Please contact him with questions or feedback.")

    st.markdown("Sorry if it takes a minute to load!")

    st.markdown("The data was last updated Feb 16, 2026.")
    
    # Load data
    contacts = load_contacts()
    locations = aggregate_by_location(contacts)
    
    # Create DataFrame for PyDeck
    df = pd.DataFrame([
        {
            'lat': loc['lat'],
            'lon': loc['lon'],
            'people_count': len(loc['people']),
            'tooltip': create_tooltip_html(loc),
            'people': loc['people']  # Store for sidebar
        }
        for loc in locations
    ])
    
    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Therapists", len(contacts))
    with col2:
        st.metric("Cities", len(locations))
    
    # Create PyDeck layer
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[lon, lat]',
        #get_radius=20000,  # Radius in meters
        radius_units="pixels",
        radius_min_pixels=10,      # never smaller than 3px
        radius_max_pixels=50,
        get_fill_color=[255, 0, 0, 160],
        pickable=True,
        auto_highlight=True,
    )
    
    # Set initial view state (centered on data)
    if len(df) > 0:
        view_state = pdk.ViewState(
            latitude=df['lat'].mean(),
            longitude=df['lon'].mean(),
            zoom=2,
            pitch=0,
        )
    else:
        view_state = pdk.ViewState(
            latitude=37.7749,
            longitude=-122.4194,
            zoom=2,
        )
    
    # Create deck
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style='road',
        tooltip={
            'html': '{tooltip}',
            'style': {
                'backgroundColor': 'white',
                'color': 'black',
                'padding': '10px',
                'borderRadius': '5px',
                'maxWidth': '400px'
            }
        }
    )
    
    # Display map
    st.pydeck_chart(deck)
    
    # Sidebar with all contacts
    with st.sidebar:
        st.header("All Contacts")
        
        search = st.text_input("🔍 Search", placeholder="Name, email, ...")
        
        for loc in locations:
 
            if search:
                search_text_loc = ''.join([
                    f"{person['name']} {person['email']}".lower()
                    for person in loc['people']
                ])
                if search.lower() not in search_text_loc: continue
            
            with st.expander(f"📍 {loc['city']} ({len(loc['people'])} people)"):
                for person in loc['people']:
                    # Filter by search
                    if search:
                        search_text = f"{person['name']} {person['email']}".lower()
                        if search.lower() not in search_text:
                            continue
                    
                    st.markdown(f"**{person['name']}**")
                    if person['email']:
                        st.markdown(f"📧 {person['email']}")
                    if person['degree']:
                        st.markdown(f"🎓 {person['degree']}")
                    st.markdown("---")

if __name__ == "__main__":
    main()
