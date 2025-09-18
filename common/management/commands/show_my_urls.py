import re
from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver

class Command(BaseCommand):
    help = 'Displays all project URLs, their methods, and parameters.'

    def handle(self, *args, **options):
        resolver = get_resolver()
        all_urls = []
        self._list_urls(resolver.url_patterns, all_urls)

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("          AVAILABLE API ENDPOINTS          ")
        self.stdout.write("=" * 80)
        self.stdout.write(f"{'HTTP METHODS'.ljust(25)} URL PATH")
        self.stdout.write("-" * 80)

        for url_info in sorted(all_urls, key=lambda x: x['path']):
            methods = ", ".join(url_info['methods']) if url_info['methods'] else "N/A"
            # <uuid:pk> 같은 파라미터를 강조 표시합니다.
            path_with_params = re.sub(r'(<\w+:\w+>)', r'[\1]', url_info['path'])
            self.stdout.write(f"[{methods.ljust(23)}] {path_with_params}")

        self.stdout.write("=" * 80 + "\n")

    def _list_urls(self, patterns, url_list, prefix=''):
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # URL 경로를 정규화하여 /로 시작하도록 보장
                path = '/' + (prefix + str(pattern.pattern)).replace('^', '').replace('$', '')
                
                view_class = getattr(pattern.callback, 'cls', None)
                methods = []
                if view_class:
                    # DRF APIView 또는 Django View의 http_method_names 속성 우선 확인
                    allowed_methods = getattr(view_class, 'http_method_names', [])
                    # 만약 http_method_names가 없다면, 직접 메소드 존재 여부 확인
                    if not allowed_methods:
                        allowed_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
                    
                    methods = [m.upper() for m in allowed_methods if hasattr(view_class, m)]
                
                url_list.append({
                    'path': path,
                    'methods': sorted(list(set(methods))), # 중복 제거 후 정렬
                })

            elif isinstance(pattern, URLResolver):
                # include()로 포함된 URL들을 재귀적으로 탐색
                new_prefix = prefix + str(pattern.pattern)
                self._list_urls(pattern.url_patterns, url_list, new_prefix)
