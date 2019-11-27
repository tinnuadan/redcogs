from ..src.shopmanager import ShopManager, SearchKey
from ..src.shop import Shop
from .helper_backend import HelperBackend


def test_shopmanager():
  backend = HelperBackend()
  mgr = ShopManager(backend)
  shop = Shop()
  otherShop = Shop()
  assert shop == mgr.addShop(shop)
  assert shop == mgr.removeShop(shop)
  assert otherShop == mgr.updateShop(shop, otherShop)
  assert None == mgr.searchShop("nothing", SearchKey.Any)
  assert mgr.getShop(10).id == 10