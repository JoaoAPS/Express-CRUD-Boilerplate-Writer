Express CRUD Boilerplate Writer
===============================

A script that creates the boilerplate of the common layers used on express projects for a given model.
The layers considered are `model`, `repository`, `service`, `controller` and `route`.

## Usage

``` shell
python create-express-crud.py <model_name> <model_name_plural>
```

## What does it do

Given the name and the name's plural of the model (for example "person", "people") the following files are created:

- `models/person.model.ts`: Sequelize model with interfaces
- `repositories/person.repository.ts`: Repository that translates from sequelize model to interfaces
- `services/person.service.ts`: Services
- `controllers/person.controller.ts`: Controller
- `routes/person.route.ts`: Routes

The directories must already be created on the directory you're running the script.
