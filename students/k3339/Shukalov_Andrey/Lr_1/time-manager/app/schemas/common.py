from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(max_length=5000)]


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class PatchSchema(Schema):
    nullable_fields: ClassVar[set[str]] = set()

    @model_validator(mode="after")
    def validate_patch(self) -> "PatchSchema":
        # Omitted fields are unchanged; explicit null is allowed only for nullable columns.
        if not self.model_fields_set:
            raise ValueError("Provide at least one field")
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in self.nullable_fields:
                raise ValueError(f"{name} cannot be null")
        return self
