from typing import Dict, List

class CodeHistoryManager:
    def __init__(self):
        self._code_histories: Dict[str, List[Dict]] = {}
        self._catalog_token: Dict[str, List[Dict]] = {}

    def get_code_history(self, sid: str) -> List[Dict]:
        return self._code_histories.get(sid, [])

    def add_to_code_history(self, sid: str, code: str, result: str, success: bool):
        if sid not in self._code_histories:
            self._code_histories[sid] = []
        
        self._code_histories[sid].append({
            'code': code,
            'result': result,
            'success': success
        })

    def add_token(self, sid: str, token: str):
        print(f">> storing catalog token for session {sid}")
        if sid not in self._code_histories:
            self._catalog_token[sid] = ""
        self._catalog_token[sid] = token
        
    def get_catalog_token(self, sid: str) -> str:
        return self._catalog_token.get(sid, "")

    def update_last_code_history(self, sid: str, code: str, result: str, success: bool):
        if sid in self._code_histories and self._code_histories[sid]:
            self._code_histories[sid][-1] = {
                'code': code,
                'result': result,
                'success': success
            }

    def end_session(self, sid: str):
        if sid in self._code_histories:
            del self._code_histories[sid]
            del self._catalog_token[sid]

    def clear_all_sessions(self):
        self._code_histories.clear()


code_history_manager = CodeHistoryManager()