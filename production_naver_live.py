import production_naver

# production_naver already prefers the live Naver Finance KPI100 page, then
# falls back to the newer Naver API, and finally Yahoo. Keep this module only as
# the stable Railway entrypoint so parser errors are logged with full messages.
app = production_naver.app
