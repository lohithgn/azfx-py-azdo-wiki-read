import os
import logging 
import json

import azure.functions as func
from azure.devops.credentials import BasicAuthentication
from azure.devops.connection import Connection
from types import SimpleNamespace
from azure.devops.v7_1.wiki import WikiPage

bp = func.Blueprint() 

@bp.route(route="wiki/read") 
def default_template(req: func.HttpRequest) -> func.HttpResponse: 
    logging.info('Python HTTP trigger function processed a request.') 

    authToken = os.environ.get("AzDoAuthToken")
    azDoOrgName = os.environ.get("AzDoOrgName")
    azDoProjectName = os.environ.get("AzDoProjectName")
    azDoWikiName = os.environ.get("AzDoWikiName")
    reader = WikiReader(authToken,azDoOrgName,azDoProjectName,azDoWikiName)
    pages = reader.read_wiki()
    
    return func.HttpResponse(
        json.dumps(pages),
        mimetype='application/json'
    )


class WikiReader:
        def __init__(self, auth_token: str, orgName: str, projectName: str, wikiName: str):
            self.auth_token = auth_token
            self.url = f'https://dev.azure.com/{orgName}'
            self.project = projectName
            self.wiki = wikiName
            self.__VERSION__ = "1.0.0"

        def read_wiki(self):
            context = SimpleNamespace()
            context.runner_cache = SimpleNamespace()
            context.connection = Connection(
                base_url=self.url,
                creds=BasicAuthentication('PAT', self.auth_token),
                user_agent='azdo-wiki-read/' + self.__VERSION__
            )

            wikiClient = context.connection.clients.get_wiki_client()
            getPageResponse = wikiClient.get_page(self.project, self.wiki, recursion_level='full')
            wikiPages = getPageResponse.page.sub_pages
            pages_list = []

            for page in wikiPages:
                pageData = {
                    "content":page.content,
                    "git_item_path":page.git_item_path,
                    "id":page.id,
                    "is_non_conformant":page.is_non_conformant,
                    "is_parent_page":page.is_parent_page,
                    "order":page.order,
                    "path":page.path,
                    "remote_url":page.remote_url,
                    "url":page.url
                }
                pages_list.append(pageData)
            return pages_list