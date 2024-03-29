# Copyright 2019 - 2021 AngrySoft Sebastian Zwierzchowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "0.4"

__all__ = [
    'Server',
    'Client',
    'Document',
    'Database',
    'UrllibConn',
    'ServerError',
    'DatabaseError',
    'DocumentError']

from .server import Server
from .client import Client
from .db import Database
from .doc import Document
from .exceptions import ServerError, DatabaseError, DocumentError
