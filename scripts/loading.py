import requests
from pathlib import Path
from tqdm.auto import tqdm
import pandas as pd
import gzip
import json



def load_wellcome_data(n_samples=10000, data_dir="./data", force_download=False):
    """
    Download and load Wellcome Collection works data (reads directly from gzipped file).
    Extracts ALL available fields without filtering.
    
    Parameters:
    -----------
    n_samples : int, default=10000
        Number of samples to load into DataFrame. Use None to load all data.
    data_dir : str, default="./data"
        Directory to store downloaded data
    force_download : bool, default=False
        If True, re-download even if file exists
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing all available parsed works data
    """
    
    snapshot_url = "https://data.wellcomecollection.org/catalogue/v2/works.json.gz"
    data_dir = Path(data_dir).resolve()
    data_dir.mkdir(exist_ok=True)
    
    file_name = Path(snapshot_url).parts[-1]
    zipped_path = data_dir / file_name
    
    # Download if needed
    if force_download or not zipped_path.exists():
        print(f"Downloading {file_name}...")
        r = requests.get(snapshot_url, stream=True)
        download_progress_bar = tqdm(
            unit="B",
            total=int(r.headers["Content-Length"]),
            desc=f"downloading {file_name}",
        )
        with open(zipped_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    download_progress_bar.update(len(chunk))
        download_progress_bar.close()
    else:
        print(f"Using existing file: {zipped_path}")
    
    # Parse JSON lines directly from gzipped file
    print(f"Loading {'all' if n_samples is None else n_samples} samples from {file_name}...")
    
    works = []
    with gzip.open(zipped_path, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc="Parsing JSON lines", total=n_samples)):
            if n_samples is not None and i >= n_samples:
                break
                
            try:
                work = json.loads(line)
                parsed = extract_all_fields(work)
                works.append(parsed)
                
            except json.JSONDecodeError:
                continue
    
    # Create DataFrame
    df = pd.DataFrame(works)
    
    print(f"\n{'='*60}")
    print(f"✓ Loaded {len(df):,} works")
    print(f"✓ DataFrame shape: {df.shape}")
    print(f"\nMissing values (count):")
    missing_summary = df.isnull().sum()
    missing_summary = missing_summary[missing_summary > 0].sort_values(ascending=False)
    if len(missing_summary) > 0:
        print(missing_summary)
    else:
        print("No missing values!")
    
    print(f"\nMissing values (percentage):")
    missing_pct = (df.isnull().sum() / len(df) * 100)
    missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)
    if len(missing_pct) > 0:
        print(missing_pct.round(2))
    
    print(f"{'='*60}\n")
    
    return df


def extract_all_fields(work):
    """
    Extract ALL available fields from a work record.
    """
    parsed = {
        # Basic info
        'id': work.get('id'),
        'title': work.get('title'),
        'alternativeTitles': None,
        'workType': work.get('workType', {}).get('label'),
        'workType_id': work.get('workType', {}).get('id'),
        'description': work.get('description'),
        'physicalDescription': work.get('physicalDescription'),
        'lettering': work.get('lettering'),
        'edition': work.get('edition'),
        
        # Production info
        'production_date': None,
        'production_date_from': None,
        'production_date_to': None,
        'production_places': [],
        'production_agents': [],
        'production_function': None,
        
        # Contributors
        'contributors': [],
        'contributor_roles': [],
        'contributor_ids': [],
        
        # Classification
        'subjects': [],
        'subject_ids': [],
        'genres': [],
        'genre_ids': [],
        
        # Languages
        'languages': [],
        'language_ids': [],
        
        # Identifiers
        'identifiers': [],
        'isbn': None,
        'issn': None,
        'sierra_system_number': None,
        'wellcome_library_number': None,
        
        # Notes
        'notes': [],
        'note_types': [],
        
        # Availability
        'thumbnail_url': None,
        'has_digitized_items': False,
        'items_count': 0,
        'availability_status': [],
        
        # Relationships
        'partOf_title': None,
        'partOf_id': None,
        'parts_count': 0,
        'precededBy_title': None,
        'precededBy_id': None,
        'succeededBy_title': None,
        'succeededBy_id': None,
        
        # Holdings
        'holdings_count': 0,
        
        # Reference number
        'referenceNumber': work.get('referenceNumber'),
        
        # Images
        'images_count': 0,
    }
    
    # Alternative titles
    alt_titles = work.get('alternativeTitles', [])
    if alt_titles:
        parsed['alternativeTitles'] = '; '.join(alt_titles)
    
    # Production info
    production = work.get('production', [])
    if production:
        prod = production[0]
        
        # Function
        if 'function' in prod:
            parsed['production_function'] = prod['function'].get('label')
        
        # Dates
        dates = prod.get('dates', [])
        if dates:
            date_obj = dates[0]
            parsed['production_date'] = date_obj.get('label')
            
            # Extract structured dates if available
            if 'range' in date_obj:
                range_obj = date_obj['range']
                parsed['production_date_from'] = range_obj.get('from')
                parsed['production_date_to'] = range_obj.get('to')
        
        # Places
        places = prod.get('places', [])
        for place in places:
            if 'label' in place:
                parsed['production_places'].append(place['label'])
        
        # Agents (publishers, etc.)
        agents = prod.get('agents', [])
        for agent in agents:
            if 'label' in agent:
                parsed['production_agents'].append(agent['label'])
    
    # Contributors with roles and IDs
    contributors = work.get('contributors', [])
    for contrib in contributors:
        agent = contrib.get('agent', {})
        if 'label' in agent:
            parsed['contributors'].append(agent['label'])
            
            # Get agent ID
            if 'id' in agent:
                parsed['contributor_ids'].append(agent['id'])
            
            # Get role
            roles = contrib.get('roles', [])
            if roles:
                role_label = roles[0].get('label', 'Unknown')
            else:
                role_label = 'Unknown'
            parsed['contributor_roles'].append(role_label)
    
    # Subjects with IDs
    subjects = work.get('subjects', [])
    for subj in subjects:
        if 'label' in subj:
            parsed['subjects'].append(subj['label'])
            if 'id' in subj:
                parsed['subject_ids'].append(subj['id'])
    
    # Genres with IDs
    genres = work.get('genres', [])
    for genre in genres:
        if 'label' in genre:
            parsed['genres'].append(genre['label'])
            if 'id' in genre:
                parsed['genre_ids'].append(genre['id'])
    
    # Languages with IDs
    languages = work.get('languages', [])
    for lang in languages:
        if 'label' in lang:
            parsed['languages'].append(lang['label'])
            if 'id' in lang:
                parsed['language_ids'].append(lang['id'])
    
    # Identifiers
    identifiers = work.get('identifiers', [])
    for ident in identifiers:
        id_type = ident.get('identifierType', {}).get('id', '')
        id_value = ident.get('value', '')
        
        if id_type and id_value:
            parsed['identifiers'].append(f"{id_type}:{id_value}")
            
            # Extract specific identifiers
            if id_type == 'isbn':
                parsed['isbn'] = id_value
            elif id_type == 'issn':
                parsed['issn'] = id_value
            elif id_type == 'sierra-system-number':
                parsed['sierra_system_number'] = id_value
            elif 'wellcome' in id_type.lower():
                parsed['wellcome_library_number'] = id_value
    
    # Notes with types
    notes = work.get('notes', [])
    for note in notes:
        note_type = note.get('noteType', {}).get('label', 'general')
        parsed['note_types'].append(note_type)
        
        contents = note.get('contents', [])
        for content in contents:
            if isinstance(content, str):
                parsed['notes'].append(content)
    
    # Thumbnail
    thumbnail = work.get('thumbnail', {})
    if thumbnail:
        parsed['thumbnail_url'] = thumbnail.get('url')
    
    # Items (availability)
    items = work.get('items', [])
    parsed['items_count'] = len(items)
    
    # Check availability and digital items
    for item in items:
        locations = item.get('locations', [])
        for loc in locations:
            # Check for digital items
            if loc.get('locationType', {}).get('id') == 'online':
                parsed['has_digitized_items'] = True
            
            # Get availability status
            access_conditions = loc.get('accessConditions', [])
            for condition in access_conditions:
                if 'status' in condition:
                    status = condition['status'].get('label')
                    if status:
                        parsed['availability_status'].append(status)
    
    # Holdings
    holdings = work.get('holdings', [])
    parsed['holdings_count'] = len(holdings)
    
    # Relationships - partOf
    if 'partOf' in work and work['partOf']:
        part_of = work['partOf'][0]
        parsed['partOf_title'] = part_of.get('title')
        parsed['partOf_id'] = part_of.get('id')
    
    # Relationships - parts
    parts = work.get('parts', [])
    parsed['parts_count'] = len(parts)
    
    # Relationships - precededBy
    if 'precededBy' in work and work['precededBy']:
        preceded = work['precededBy'][0]
        parsed['precededBy_title'] = preceded.get('title')
        parsed['precededBy_id'] = preceded.get('id')
    
    # Relationships - succeededBy
    if 'succeededBy' in work and work['succeededBy']:
        succeeded = work['succeededBy'][0]
        parsed['succeededBy_title'] = succeeded.get('title')
        parsed['succeededBy_id'] = succeeded.get('id')
    
    # Images
    images = work.get('images', [])
    parsed['images_count'] = len(images)
    
    # Convert lists to strings for DataFrame
    parsed['production_places'] = '; '.join(parsed['production_places']) if parsed['production_places'] else None
    parsed['production_agents'] = '; '.join(parsed['production_agents']) if parsed['production_agents'] else None
    parsed['contributors'] = '; '.join(parsed['contributors']) if parsed['contributors'] else None
    parsed['contributor_roles'] = '; '.join(parsed['contributor_roles']) if parsed['contributor_roles'] else None
    parsed['contributor_ids'] = '; '.join(parsed['contributor_ids']) if parsed['contributor_ids'] else None
    parsed['subjects'] = '; '.join(parsed['subjects']) if parsed['subjects'] else None
    parsed['subject_ids'] = '; '.join(parsed['subject_ids']) if parsed['subject_ids'] else None
    parsed['genres'] = '; '.join(parsed['genres']) if parsed['genres'] else None
    parsed['genre_ids'] = '; '.join(parsed['genre_ids']) if parsed['genre_ids'] else None
    parsed['languages'] = '; '.join(parsed['languages']) if parsed['languages'] else None
    parsed['language_ids'] = '; '.join(parsed['language_ids']) if parsed['language_ids'] else None
    parsed['identifiers'] = '; '.join(parsed['identifiers']) if parsed['identifiers'] else None
    parsed['notes'] = ' | '.join(parsed['notes']) if parsed['notes'] else None
    parsed['note_types'] = '; '.join(parsed['note_types']) if parsed['note_types'] else None
    parsed['availability_status'] = '; '.join(set(parsed['availability_status'])) if parsed['availability_status'] else None
    
    return parsed

