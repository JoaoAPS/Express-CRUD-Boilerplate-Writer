#!/bin/python

import sys
from pathlib import Path
from textwrap import dedent


MODEL_TEXT = dedent("""\
    import {{ Table, Model, Column }} from "sequelize-typescript"

    interface Base{Name} {{
      id: number
      ...
    }}

    interface {Name} extends Base{Name} {{
      ...
    }}

    interface {Name}Detail extends Base{Name} {{
      ...
    }}

    type {Name}Preview = Base{Name}

    type {Name}Input = Omit<Base{Name}, "id">

    interface {Name}ModelAttributes extends Base{Name} {{
      ...
    }}

    interface {Name}CreationAttributes extends Omit<Base{Name}, "id"> {{
      ...
    }}

    @Table({{ timestamps: false, tableName: "{name_plural}" }})
    class {Name}Model extends Model<{Name}ModelAttributes, {Name}CreationAttributes> {{
      @Column
      name!: string
    
      ...
    }}

    export {{ {Name}Model, {Name}, {Name}Detail, {Name}Preview, {Name}Input }}
    export default {Name}Model
    
""")


REPOSITORY_TEXT = dedent("""\
    import {{ {Name}, {Name}Detail, {Name}Input, {Name}Model }} from "../models/{name}.model"

    async function get{NamePlural}(): Promise<{Name}[]> {{
      const {name_plural} = await {Name}Model.findAll({{ order: "id" }})
      return {name_plural}.map({name}ModelTo{Name})
    }}

    async function get{Name}(id: number): Promise<{Name}Detail | null> {{
      const {name} = await {Name}Model.findByPk(id)
      if (!{name}) return null
      return {name}ModelTo{Name}Detail({name})
    }}

    async function create{Name}({name}Input: {Name}Input): Promise<{Name}Detail> {{
      const {name} = await {Name}Model.create({name}Input)
      return {name}ModelTo{Name}Detail({name})
    }}

    async function update{Name}(id: number, {name}Input: {Name}Input): Promise<void> {{
      await {Name}Model.update({name}Input, {{ where: {{ id }} }})
    }}

    async function delete{Name}(id: number): Promise<void> {{
      await {Name}Model.destroy({{ where: {{ id }} }})
    }}

    function {name}ModelTo{Name}({name}Model: {Name}Model): {Name} {{
      const base = {name}Model.toJSON()
      return {{ ...base }}
    }}

    function {name}ModelTo{Name}Detail({name}Model: {Name}Model): {Name}Detail {{
      const base = {name}Model.toJSON()
      return {{ ...base }}
    }}
    
    export default {{ get{NamePlural}, get{Name}, create{Name}, update{Name}, delete{Name} }}
    
""")


SERVICE_TEXT = dedent("""\
    import {{ {Name}, {Name}Detail, {Name}Input }} from "../models/{name}.model"
    import {name}Repository from "../repositories/{name}.repository"

    async function get{NamePlural}(): Promise<{Name}[]> {{
      return await {name}Repository.get{NamePlural}()
    }}

    async function get{Name}(id: number): Promise<{Name}Detail | null> {{
      return await {name}Repository.get{Name}(id)
    }}

    async function create{Name}({name}: {Name}Input): Promise<{Name}Detail> {{
      return await {name}Repository.create{Name}({name})
    }}

    async function update{Name}(id: number, {name}: {Name}Input): Promise<void> {{
      await {name}Repository.update{Name}(id, {name})
    }}

    async function delete{Name}(id: number): Promise<void> {{
      await {name}Repository.delete{Name}(id)
    }}

    export default {{ get{NamePlural}, get{Name}, create{Name}, update{Name}, delete{Name} }}
    
""")


CONTROLLER_TEXT = dedent("""\
    import {{ RequestHandler, Request }} from "express"
    import {{ body, validationResult }} from "express-validator"

    import {name}Service from "../services/{name}.service"
    import {{ parseId }} from "../utils/params"
    import {{ getResponseError }} from "../utils/error"

    const get{NamePlural}: RequestHandler = async (req, res, next) => {{
      try {{
        const {name_plural} = await {name}Service.get{NamePlural}()
        res.send({name_plural})
      }} catch (err) {{
          next(err)
      }}
    }}

    const get{Name}: RequestHandler = async (req, res, next) => {{
      try {{
        const id: number = parseId(req.params.id)
        const {name} = await {name}Service.get{Name}(id)
        if ({name} === null) throw getResponseError(404, "Not Found")
        res.send({name})
      }} catch (err) {{
        next(err)
      }}
    }}

    const create{Name}: RequestHandler = async (req, res, next) => {{
      try {{
        await validate{Name}Payload(req)
        const payload = {{ ... }}
        const {name} = await {name}Service.create{Name}(payload)
        res.send({name})
      }} catch (err) {{
        next(err)
      }}
    }}

    const update{Name}: RequestHandler = async (req, res, next) => {{
      try {{
        const id: number = parseId(req.params.id)
        const {name} = await {name}Service.get{Name}(id)
        if ({name} === null) throw getResponseError(404, "Not Found")

        await validate{Name}Payload(req)
        const payload = {{ ... }}
        await {name}Service.update{Name}(id, payload)
        const updated{Name} = await {name}Service.get{Name}(id)
        res.send(updated{Name})
      }} catch (err) {{
        next(err)
      }}
    }}

    const delete{Name}: RequestHandler = async (req, res, next) => {{
      try {{
        const id: number = parseId(req.params.id)
        const {name} = await {name}Service.get{Name}(id)
        if ({name} === null) throw getResponseError(404, "Not Found")

        await {name}Service.delete{Name}(id)
        res.status(204).end()
      }} catch (err) {{
        next(err)
      }}
    }}

    async function validate{Name}Payload(req: Request): Promise<void> {{
      const validations = [
        body("name").isString.isLength({{ min: 1 }}).withMessage("Please provide a valid name."),
        ...
      ]
      await Promise.all(validations.map(validation => validation.run(req))
      const errors = validationResult(req)
      if (!errors.isEmpty()) throw getResponseError(400, errors.array())
    }}

    export default {{ get{NamePlural}, get{Name}, create{Name}, update{Name}, delete{Name} }}
    
""")


ROUTE_TEXT = dedent("""\
    import {{ Router }} from "express"

    import {name}Controller from "../controllers/{name}.controller"

    const router = Router()

    router.get("/", {name}Controller.get{NamePlural})
    router.post("/", {name}Controller.create{Name})
    router.get("/:id", {name}Controller.get{Name})
    router.put("/:id", {name}Controller.update{Name})
    router.delete("/:id", {name}Controller.delete{Name})

    export default router
    
""")


FILEPATHS = {
    'model': 'models/{name}.model.ts',
    'repository': 'repositories/{name}.repository.ts',
    'service': 'services/{name}.service.ts',
    'controller': 'controllers/{name}.controller.ts',
    'route': 'routes/{name}.route.ts',
}


FILE_CONTENTS = {
    'model': MODEL_TEXT,
    'repository': REPOSITORY_TEXT,
    'service': SERVICE_TEXT,
    'controller': CONTROLLER_TEXT,
    'route': ROUTE_TEXT,
}


def _lower_first(string: str) -> str:
    return string[0].lower() + string[1:]


def _upper_first(string: str) -> str:
    return string[0].upper() + string[1:]


def _check_for_filepath_errors(filepath: str) -> None:
    fp = Path(filepath)
    if fp.exists():
        raise ValueError(f'File "{filepath}" already exists!')
    
    directory = Path(fp.parts[0])
    if not directory.exists() or not directory.is_dir():
        raise ValueError(
            f'Error: "{directory}" is not a directory! '
            'Make sure you ran the script on the correct folder.'
        )


def main() -> None:
    [script_name, *args] = sys.argv
    argument_error = \
        f"Usage:\n\tpython {script_name} <model_name> <model_name_plural>"
    if len(args) < 2:
        print(argument_error)
        return

    name = _lower_first(args[0])
    name_plural = _lower_first(args[1])
    Name = _upper_first(args[0])
    NamePlural = _upper_first(args[1])

    for filepath in FILEPATHS.values():
        _check_for_filepath_errors(filepath)

    for key, str_filepath in FILEPATHS.items():
        filepath = Path(str_filepath.format(name=name))
        file_content = FILE_CONTENTS[key].format(
            name=name,
            name_plural=name_plural,
            Name=Name,
            NamePlural=NamePlural
        )
        with open(filepath, 'w') as file:
            file.write(file_content)


if __name__ == '__main__':
    main()
