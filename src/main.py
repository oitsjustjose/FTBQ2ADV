"""
AUTHOR: Jose Stovall | oitsjustjose@git
LICENSE: MIT
"""
import codecs
import json
import os
from typing import Any, Dict

import snbtlib
from colorama import Fore

from advancement import Advancement
from param_parser import CommandlineConfigParser

Json: type = Dict[str, Any]


def main(parmesan: CommandlineConfigParser) -> None:
    """Main func which uses the confparser to build adv. JSONs from a quest SNBT"""
    infile = parmesan.get_argument("input")
    namespace = parmesan.get_argument("namespace") or "minecraft"

    with open(infile, "r", encoding="utf-8") as file_handle:
        data: Json = snbtlib.loads(file_handle.read())  # type: ignore

    idmp = build_id_filename_mapping(data)
    for quest in data["quests"]:
        advancement = create_adv_from_quest(quest, namespace, idmp)
        with codecs.open(
            f'./out/{idmp[quest["id"]]}.json', "w", "utf-8"
        ) as file_handle:
            data_as_str = (
                json.dumps(advancement, indent=2)
                # Fix \\& -> \\§ -> &
                .replace("\\\\\\u00a7", "&")
                # Fix \u00a7 -> §
                .replace("\\u00a7", "§")
                # Fix \\\ -> \
                .replace("\\\\\\", "\\")
            )
            file_handle.write(data_as_str)


def create_adv_from_quest(quest: Json, namespace: str, idmp: Dict[str, str]) -> Json:
    """Creates an advancement from a singular quest"""
    adv = Advancement(quest, namespace, idmp)
    errors = adv.get_validation_errors()
    if errors:
        print(f"\n{'-'*os.get_terminal_size().columns}\n")
        print(
            f"{Fore.YELLOW}[i] Validation Errors for Quest '{idmp[quest['id']]}' were found:{Fore.RESET}"
        )
        for error in errors:
            print(f"    • {error}")
    return adv.to_json()


def build_id_filename_mapping(data: Json) -> Dict[str, str]:
    """Creates a mapping of FTB Quest Id to the filename generated by yours truly"""
    id_to_filename_mapping: Dict[str, str] = {}

    for quest in data["quests"]:
        file_name_root: str = f"{quest['id']}"
        # user-defined title
        if "title" in quest:
            try:  # some titles are json colored
                file_name_root: str = json.loads(quest["title"].replace('\\"', '"'))[
                    "text"
                ]
            except json.decoder.JSONDecodeError:
                file_name_root = quest["title"]
        else:
            for task in quest["tasks"]:
                if task["item"]:
                    file_name_root: str = task["item"].split(":")[1]
                    break
        file_name_root: str = file_name_root.replace(" ", "_").replace("-", "_").lower()
        id_to_filename_mapping[quest["id"]] = file_name_root
    return id_to_filename_mapping


if __name__ == "__main__":
    if not os.path.exists("./out"):
        os.mkdir("./out")

    main(
        CommandlineConfigParser(
            required_args={"input": str}, optional_args={"namespace": str}
        )
    )
