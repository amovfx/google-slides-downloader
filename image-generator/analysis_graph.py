import operator
from typing import Annotated, Any, List, Any

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from .prompt_generator import Summarizer, ArtDirector, LeonardoPrompt
import pathlib
import yaml
import pandas as pd
import json
from .image_graph import image_graph


class InputState(TypedDict):
    file_path: str | pathlib.Path


class OutputState(TypedDict):
    art_direction: str
    deck_summary: str
    image_paths: List[str]


class GraphState(InputState, OutputState):
    aggregate: Annotated[list, operator.add]
    file_contents: str
    prompt_input: Any


def read_deck(state: GraphState):
    print("reading")
    file_contents = pathlib.Path(state["file_path"]).read_text()

    return {"file_contents": file_contents}


def summarize_deck(state: GraphState):
    print("summaraizeing")
    summarizer = Summarizer().make_runnable()
    return summarizer.invoke(state["file_contents"])


def art_direct(state: GraphState):
    print("art direction")
    art_director = ArtDirector().make_runnable()
    return art_director.invoke(state["file_contents"])


def prep_image_inputs(state: GraphState):
    data = yaml.safe_load(state["file_contents"])
    slides = [json.dumps(d) for d in data]
    output_paths = [
        pathlib.Path(state["file_path"]).parent / f"images/image_{i+1}.jpg"
        for i, _ in enumerate(slides)
    ]
    filtered_items = [
        (slide, path) for slide, path in zip(slides, output_paths) if not path.exists()
    ]

    # Unpack the filtered items back into separate lists
    slides, output_paths = zip(*filtered_items) if filtered_items else ([], [])

    data = pd.DataFrame()
    data["slide"] = slides
    data["output_path"] = output_paths
    data["art_direction"] = state["art_direction"]
    data["deck_summary"] = state["deck_summary"]

    image_data = data.to_dict(orient="records")

    return {"prompt_input": image_data}


def make_images(state: GraphState):
    result = image_graph.batch(state["prompt_input"])
    return {"image_paths": [r["downloaded_path"] for r in result]}

    # image_generator = ImageGenerator.batch(image_data)


workflow = StateGraph(GraphState, input=InputState, output=OutputState)
workflow.add_node(read_deck)
workflow.add_node(summarize_deck)
workflow.add_node(art_direct)
workflow.add_node(prep_image_inputs)
workflow.add_node(make_images)
workflow.add_edge("read_deck", "summarize_deck")
workflow.add_edge("read_deck", "art_direct")


workflow.add_edge("summarize_deck", "prep_image_inputs")
workflow.add_edge("art_direct", "prep_image_inputs")
workflow.add_edge("prep_image_inputs", "make_images")
workflow.set_entry_point("read_deck")
workflow.set_finish_point("make_images")
graph = workflow.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {
            "file_path": "/Users/andrew/git/google-slides-downloader/slides/src/data/01_Intro/manifest.yml"
        }
    )
    print(result)
