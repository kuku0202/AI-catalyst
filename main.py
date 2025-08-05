from client import MCPClient
import os




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
        return mcp_response
    
    
