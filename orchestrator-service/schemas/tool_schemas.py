# schemas/tool_schemas.py

#from dataclasses import dataclass
# from typing import Dict, Type


# @dataclass
# class ToolSchema:
#     name: str
#     required_args: Dict[str, Type]
#     allow_extra_args: bool = False


# TOOL_SCHEMAS = {
#     "get_time": ToolSchema(
#         name="get_time",
#         required_args={}
#     ),

#     "search_docs": ToolSchema(
#         name="search_docs",
#         required_args={
#             "query": str
#         }
#     )
# }


TOOL_SCHEMAS = {

 "get_time": {},

   "search_docs": {
       "query": str
   }

}