from abc import ABC, abstractmethod
import datetime
from typing import List
from apis import *
from writers import *

class DataIngestor(ABC):
    
    def __init__(self,writer: DataWriter, coins: List[str], default_start_date: datetime.date) -> None:
        self.default_start_date = default_start_date
        self.coins = coins
        self.writer = writer
        self._checkpoint = None
    
    @property   
    def _checkpoints_filename(self) -> str:
        return f"{self.__class__.__name__}.checkpoint"
    
    def _write_checkpoint(self):
        with open(self._checkpoints_filename,'w') as f:
            f.write(f"{self._checkpoint}")
            
    def _load_checkpoint(self) -> datetime:
        try:
            with open(self._checkpoints_filename,'r') as f:
                return datetime.datetime.strptime(f.read(),"%Y-%m-%d").date()
        except FileNotFoundError:
            return None
        
    def _get_checkpoint(self):
        if not self._checkpoint:
            return self.default_start_date
        else:
            return self._checkpoint
        
    def _update_checkpoint(self,value):
        self._checkpoint = value
        self._write_checkpoint()
        
    @abstractmethod
    def ingest(self) -> None:
        pass
  
class DaySummaryIngestor(DataIngestor):
    def ingest(self) -> None:
        date = self._get_checkpoint()
        if date < datetime.date.today():
            for coin in self.coins:
                api = DaySummaryApi(coin=coin)
                data = api.get_data(date=date)
                self.writer(coin=coin,api=api.type).write(data)
            self._update_checkpoint(date + datetime.timedelta(days=1))