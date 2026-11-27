// Bust desk Page localStorage cache when this app's page assets change.
// Without developer_mode, Frappe keeps `_page:<name>` forever, so Scan→Re-scan
// and page CSS never update after a code change.
(function () {
	const PAGE = "invoice-delivery-period-reconciliation";
	const VER_KEY = "invoice_delivery_match_page_assets_v";
	const VER = "13";
	try {
		if (localStorage.getItem(VER_KEY) !== VER) {
			localStorage.removeItem("_page:" + PAGE);
			localStorage.setItem(VER_KEY, VER);
		}
	} catch (e) {
		// ignore quota / private mode
	}
})();
