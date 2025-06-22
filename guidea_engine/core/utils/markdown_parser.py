import frontmatter
import re

def extract_locations_from_document(document: str):
    post = frontmatter.loads(document)
    loc_map = post.get('loc_map', {})
    body = post.content

    locations = []
    for slug, heading in loc_map.items():
        pattern = re.escape(heading.strip())
        if re.search(rf'^{pattern}', body, re.MULTILINE):
            locations.append({
                'slug': slug,
                'name': heading.lstrip('# ').strip()
            })
    return locations
