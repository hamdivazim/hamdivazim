import os
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_projects():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "page_size": 3,
        "sorts": [{"property": "date", "direction": "descending"}]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("results", [])

def format_tags(tags):
    return " ".join([f"<code>{tag['name']}</code>" for tag in tags])

def format_img(img, name, url):
    return f'<a href="{url}"><kbd><img src="{img}" alt="{name} Thumbnail" width="250"></kbd></a>'

def update_readme():
    projects = get_projects()
    markdown_content = ""
    
    for p in projects:
        props = p["properties"]
        name = props["name"]["title"][0]["plain_text"]
        desc = props["description"]["rich_text"][0]["plain_text"]
        tags = format_tags(props["tags"]["multi_select"])
        url = props["url"]["url"] or "#"
        img = ""
        
        if props.get("thumbnail") and props["thumbnail"].get("url"):
            img = format_img(props["thumbnail"]["url"], name, url)

        repo = ""

        if props.get("repo"):
            r = props["repo"]["url"]
            repo = f'<p><a href="https://github.com/{r}"><img src="https://raw.githubusercontent.com/primer/octicons/main/icons/repo-16.svg" width="16" height="16" style="vertical-align: middle;"> <b>See Repository</b></a></p>'
        
        markdown_content += f"""
<table>
  <tr>
    <td width="1000">
      {img}
      <h4><a href="{url}">{name}</a></h4>
      {tags}
      <p>{desc}</p>
      {repo}
    </td>
  </tr>
</table>
"""

    with open("README.md", "r") as f:
        readme = f.read()

    start_marker = "### 🚀 Featured Projects"
    end_marker = "_Automated via GitHub Actions by fetching from Notion!_"
    
    new_readme = readme.split(start_marker)[0] + start_marker + "\n" + markdown_content + "\n" + end_marker + readme.split(end_marker)[1]

    with open("README.md", "w") as f:
        f.write(new_readme)

if __name__ == "__main__": update_readme()