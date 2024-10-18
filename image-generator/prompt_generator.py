from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
from langchain_core.runnables import ConfigurableField
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from typing import Any, Type

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")


def get_model():
    return ChatAnthropic(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model=os.getenv("CLAUDE_MODEL"),
        temperature=0.0,
        verbose=True,
        max_tokens=4096,
    ).configurable_fields(
        temperature=ConfigurableField(
            id="temperature",
            name="LLM Temperature",
            description="The temperature of the LLM",
        ),
        model=ConfigurableField(
            id="model",
            name="LLM Model Name",
            description="The name of the LLM model",
        ),
    )


class OutputModel(BaseModel):
    prompt: str = Field(
        description="The full prompt for leonardo.ai to create a image for a slide deck."
    )


import re


def extract_variables_from_template_string(template_string: str):
    """Extracts variables from a template string.

    Args:
        template_string (str): The template string to extract variables from.

    Returns:
        list: A list of variable names found in the template string.

    Raises:
        ValueError: If a variable contains whitespace.
    """
    # ...
    pattern = re.compile(r"\{(.*?)\}")
    variables = pattern.findall(template_string)
    for variable in variables:
        if " " in variable:
            raise ValueError(f"Variable {variable} should not contain whitespace")
    return variables


class CRunable(BaseModel):
    template_string: str
    model: Any = Field(default_factory=get_model)
    output_model: Type[BaseModel]

    def make_prompt_template(self):
        return PromptTemplate(
            input_variables=extract_variables_from_template_string(
                self.template_string
            ),
            template=self.template_string,
        )

    def make_runnable(self):
        return (
            self.make_prompt_template()
            | self.model.with_structured_output(self.output_model)
            | (lambda x: x.model_dump())
        )


class Summarizer(CRunable):
    template_string: str = Field(
        default="""Summarize the following pitch deck for an ai bitcoin startup. \n<deck>{deck}</deck>"""
    )

    class output_model(BaseModel):
        deck_summary: str = Field(description="The summary of the presentation deck.")


class ArtDirector(CRunable):
    template_string: str = Field(
        default="""Create artistic guidelines for illustrations for the following deck. The style should be futuristic and have elements of Miyazaki and Syd Mead <deck>{deck}</deck>"""
    )

    class output_model(BaseModel):
        art_direction: str = Field(
            description="Artistic guidelines for illustrations on the presentation deck. Keep it consice, under 1500 characters."
        )


class LeonardoPrompt(CRunable):

    class output_model(BaseModel):
        prompt: str = Field(
            description="Prompt for leonardo.ai. Keep it consice, under 1200 characters."
        )

    template_string: str = Field(
        default="""Make a prompt for leonardo.ai for an illustration for the slide.
        Use the summary to keep an overal idea of what the presentation is about.
        And the art_direction notes to craft the prompt.
        
<slide>
{slide}
</slide>

<summary>
{deck_summary}
</summary>

<art_direction>
{art_direction}   
</art_direction>

"""
    )


class LeonardoPromptEditor(CRunable):

    class output_model(BaseModel):
        prompt: str = Field(
            description="The shortend prompt for leonardo.ai. Keep it consice, under 1500 characters."
        )

    template_string: str = Field(
        default="""The following prompt is {number_of_characters} and needs to be under 1500.
        Reduce the prompt's length to get within that range.
        
<prompt>
{prompt}
</prompt>

"""
    )


class StateGraph:
    deck: str
    art_direction: str
    deck_summary: str
    prompt: str
