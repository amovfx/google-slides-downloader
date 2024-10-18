import operator
from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from pydantic import BaseModel

from .prompt_generator import (
    Summarizer,
    ArtDirector,
    LeonardoPrompt,
    LeonardoPromptEditor,
)
from .image_generator import make_image
import pathlib
import yaml

import os
import requests
from urllib.parse import urlparse
import aiohttp
import asyncio


class InputState(TypedDict):
    slide: str
    output_path: pathlib.Path
    art_direction: str
    deck_summary: str


class OutputState(TypedDict):
    downloaded_path: str | pathlib.Path


class GraphState(InputState, OutputState):
    aggregate: Annotated[list, operator.add]
    prompt: str
    deck: str
    generation_id: str
    generattions: List[str]


def make_prompt(state: GraphState):
    prompt_generator = LeonardoPrompt().make_runnable()
    return prompt_generator.invoke(state)


def edit_prompt(state: GraphState):
    prompt_editor = LeonardoPromptEditor().make_runnable()
    prompt = state["prompt"]
    return prompt_editor.invoke({"number_of_characters": len(prompt), "prompt": prompt})


def leonardo(state: GraphState):
    result = make_image(state["prompt"], state["output_path"])
    return {"downloaded_path": result}


workflow = StateGraph(GraphState, input=InputState, output=OutputState)
workflow.add_node(make_prompt)
workflow.add_node(edit_prompt)
workflow.add_node(leonardo)

workflow.add_conditional_edges(
    "make_prompt",
    lambda x: "edit" if len(x["prompt"]) > 1500 else "continue",
    {"edit": "edit_prompt", "continue": "leonardo"},
)

workflow.set_entry_point("make_prompt")
workflow.set_finish_point("leonardo")

image_graph = workflow.compile()
