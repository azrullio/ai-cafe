[out:json][timeout:180][bbox:-7.36,112.59,-7.18,112.83];
(
  nwr["name"~"warkop|warung kopi|sedulur tunggal|\bSTK\b|kedai|kopi|coffee|cafe|kafe|depot",i][!"amenity"];
  nwr["name"~"warkop|warung kopi|sedulur tunggal|\bSTK\b|kedai|kopi|coffee|cafe|kafe",i]["amenity"!~"^(cafe|restaurant|fast_food|food_court|ice_cream)$"]["amenity"];
);
out center tags;
