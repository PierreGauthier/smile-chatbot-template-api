from typing import Union, List, Dict

VectorInputPageContentType = Dict[str, Union[str, int, bool, List[Union[str, int]], Dict[str, Union[str, int, bool, List[Union[str, int]]]]]]
VectorizedPageContentType = Dict[str, Union[str, int, bool, List[Union[str, int]], Dict[str, Union[str, int, bool, List[Union[str, int]]]], List[float]]]