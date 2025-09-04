from client import MCPClient, extract_json_between_markers
import os
import json
from mp_api.client import MPRester




class CatalystAgent:
    def __init__(self, web_search, query):
        self.prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.web_search = web_search
        self.query = query
        
    async def call_google_scholar_client(self, query):
        mcp_client = MCPClient()
        try:
            await mcp_client.connect_to_server("/home/yuesu/mail/catalyst/mcp-server/Google-Scholar-MCP-Server/google_scholar_server.py")
            response = await mcp_client.process_query(query)
            return response
        except Exception as e:
            print(f"Error in MCP client: {e}")
            return f"Error: {str(e)}"
        finally:
            try:
                await mcp_client.close()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")
    
    async def call_catalyst_hub_client(self, query):
        mcp_client = MCPClient()
        try:
            await mcp_client.connect_to_server("/home/yuesu/mail/catalyst/mcp-server/catalysishub-mcp-server/catalysishub_mcp_server.py")
            response = await mcp_client.process_query(query)
            return response
        except Exception as e:
            print(f"Error in MCP client: {e}")
            return f"Error: {str(e)}"
        finally:
            try:
                await mcp_client.close()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")
    
    def extract_elements_from_catalysts(self, catalyst_list):
        """
        Extract individual elements from catalyst formulas.
        Returns a list of lists, where each sublist contains elements from one catalyst.
        For complex formulas like "Ga-Cu/CeO2", splits by slash and creates separate lists.
        """
        import re
        all_catalyst_elements = []
        
        for catalyst in catalyst_list:
            # Split by slash first to handle cases like "Ga-Cu/CeO2"
            catalyst_parts = catalyst.split('/')
            
            for part in catalyst_parts:
                # Remove common catalyst notation characters (keep slashes for splitting)
                clean_part = re.sub(r'[\-\(\)\d]+', ' ', part)
                
                # Extract element symbols (capital letter followed by optional lowercase)
                element_matches = re.findall(r'[A-Z][a-z]?', clean_part)
                
                if element_matches:  # Only add non-empty lists
                    all_catalyst_elements.append(element_matches)
        
        return all_catalyst_elements


       
    async def run(self):
        search_prompt = open(os.path.join(self.prompt_dir, "search.txt")).read()
        search_prompt = search_prompt.format(
            query=self.query,
            web_search=self.web_search
        )
        if self.web_search == "Google-Scholar":
            mcp_response = await self.call_google_scholar_client(search_prompt)
        elif self.web_search == "Catalyst_Hub-Search":
            mcp_response = await self.call_catalyst_hub_client(search_prompt)
        else:
            raise ValueError(f"Invalid web_search: {self.web_search}")

        json_response = extract_json_between_markers(mcp_response)
        with open("output.json", "w") as f:
            json.dump(json_response, f, indent=4)
        potential_catalysts = json_response["catalyst"]
        individual_elements = self.extract_elements_from_catalysts(potential_catalysts)
        with MPRester() as mpr:
            results = []
            for element in individual_elements:
                result = mpr.materials.summary.search(
                elements=element
                )
                results.append(result)
        for result in results:
            print(result[0].material_id)
            print(result[0].structure)
        return json_response
    
    
